from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from src.config import settings
from src.models import LandbotMessage, HubSpotWebhookPayload
from src.services.hubspot_service import hubspot_service
from src.services.landbot_service import landbot_service
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug_webhooks.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Landbot-HubSpot Middleware")

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}

@app.post("/webhook/landbot-inbound")
async def landbot_inbound(request: Request, background_tasks: BackgroundTasks):
    """
    Handle incoming messages from Landbot (Human Takeover or MessageHook).
    """
    try:
        payload = await request.json()
        
        # Landbot MessageHooks send a list of messages
        messages = payload.get("messages", [])
        if not messages:
            # Fallback for direct Webhook block if used
            if "customer" in payload and "message" in payload:
                messages = [payload]
            else:
                return {"status": "ignored", "reason": "No messages found"}

        for msg_item in messages:
            # 1. Identify Sender
            sender = msg_item.get("sender", {})
            # Default to 'customer' if not specified (common in direct Webhook blocks)
            sender_type = sender.get("type") or msg_item.get("author_type") or "customer"
            
            if sender_type != "customer":
                logger.info(f"Ignoring message from {sender_type}")
                continue

            # 2. Extract Data
            customer = msg_item.get("customer", {})
            customer_id = customer.get("id")
            customer_name = customer.get("name", "Visitor")
            customer_phone = customer.get("phone")
            
            # Check if user is in "Human Takeover" mode in Landbot
            # If agent_id is present, it means a human is/was assigned
            agent_id = customer.get("agent_id")
            
            # IMPORTANT: We only bridge to HubSpot if an agent is assigned.
            # EXCEPTION: If the payload came from a direct Webhook block (not MessageHook), 
            # we assume the user explicitly wants to send this message.
            is_direct_webhook = "messages" not in payload
            
            if not agent_id and not is_direct_webhook:
                logger.info(f"Ignoring message from customer {customer_id}: No agent assigned (Bot mode)")
                continue

            # Get message text (format varies between Webhook Block and MessageHook)
            message_text = msg_item.get("message") # Webhook block / _raw
            if not message_text and "data" in msg_item:
                message_text = msg_item["data"].get("body") # MessageHook format

            if not message_text:
                continue

            logger.info(f"Processing message for HubSpot: {customer_name} ({customer_id}): {message_text}")

            # 3. Process in Background
            background_tasks.add_task(
                process_landbot_to_hubspot,
                customer_id,
                customer_name,
                customer_phone,
                message_text
            )

        return {"status": "processed"}
    except Exception as e:
        logger.error(f"❌ Error processing Landbot payload: {e}")
        return {"status": "error", "detail": str(e)}

async def process_landbot_to_hubspot(customer_id, customer_name, customer_phone, message_text):
    """
    Logic to ensure contact exists, publish message, and associate with ticket.
    """
    try:
        contact_id = None
        # 1. Ensure Contact Exists
        if customer_id:
            try:
                contact_id = hubspot_service.get_or_create_contact(customer_name, customer_phone, landbot_id=str(customer_id))
            except Exception as e:
                logger.error(f"Failed to sync contact to HubSpot: {e}")

        # 2. Publish Message
        pub_res = hubspot_service.publish_message_to_channel(
            customer_id,
            message_text,
            sender_name=customer_name,
            phone=customer_phone
        )
        
        # 3. Associate Contact with Ticket
        # HubSpot Inboxes usually create a ticket automatically for new conversations.
        # We try to find that ticket and link our contact explicitly.
        thread_id = pub_res.get("conversationsThreadId") # Correct field name in v3 response
        logger.info(f"Thread ID received: {thread_id}, Contact ID: {contact_id}")
        
        if thread_id and contact_id:
            import asyncio
            logger.info("Waiting for HubSpot to create the ticket...")
            # Wait a few seconds for HubSpot's automatic ticket creation to trigger
            await asyncio.sleep(5) 
            
            ticket_id = hubspot_service.get_thread_associated_ticket(thread_id)
            if ticket_id:
                hubspot_service.associate_contact_with_ticket(contact_id, ticket_id)
            else:
                logger.info(f"No auto-ticket found for thread {thread_id} yet. Native association might handle it if phone matched.")
        else:
            if not thread_id:
                logger.warning(f"No conversationsThreadId in HubSpot response: {pub_res}")
            if not contact_id:
                logger.warning("No contactId available (phone missing or sync failed).")

    except Exception as e:
        logger.error(f"Error in process_landbot_to_hubspot: {e}")

@app.post("/webhook/hubspot-outbound")
async def hubspot_outbound(payload: HubSpotWebhookPayload, background_tasks: BackgroundTasks):
    """
    Handle outgoing messages from HubSpot Custom Channel.
    """
    logger.info(f"Received HubSpot payload: {payload.dict()}")
    
    if payload.type == "OUTGOING_CHANNEL_MESSAGE_CREATED" or payload.type == "MESSAGE": 
        # "MESSAGE" type might appear in some contexts, but usually "OUTGOING_CHANNEL_MESSAGE_CREATED" for webhooks.
        pass
    else:
        # Ignore other events (like status updates, typing indicators if subscribed)
        return {"status": "ignored", "type": payload.type}

    # Extract Landbot ID (Thread ID or Delivery Identifier)
    landbot_id_str = None
    
    # Priority 1: Check Thread IDs (Preferred for INTEGRATION_THREAD_ID model)
    if payload.channelIntegrationThreadIds:
        for thread_id in payload.channelIntegrationThreadIds:
            if thread_id.isdigit():
                landbot_id_str = thread_id
                logger.info(f"Found Landbot ID in thread IDs: {landbot_id_str}")
                break
    
    # Priority 2: Check Recipients (Fallback/Safety)
    if not landbot_id_str:
        for recipient in payload.recipients:
            if (recipient.deliveryIdentifier and 
                recipient.deliveryIdentifier.type == "CHANNEL_SPECIFIC_OPAQUE_ID" and
                recipient.deliveryIdentifier.value.isdigit()):
                landbot_id_str = recipient.deliveryIdentifier.value
                logger.info(f"Found Landbot ID in recipients: {landbot_id_str}")
                break

    if not landbot_id_str:
        logger.warning(f"Could not identify Landbot Customer ID from payload. Threads: {payload.channelIntegrationThreadIds}, Recipients: {payload.recipients}")
        return {"status": "ignored", "reason": "No valid Landbot ID found"}

    try:
        landbot_id = int(landbot_id_str)
        
        message_text = payload.message.text or payload.message.richText
        # Optional: Handle rich text or attachments if needed in future
        
        if not message_text:
            logger.warning("Empty message text received.")
            return {"status": "ignored", "reason": "Empty text"}

        # Send to Landbot
        background_tasks.add_task(
            landbot_service.send_text_message,
            landbot_id,
            message_text
        )
        
        return {"status": "sent"}
        
    except ValueError:
        logger.error(f"Invalid Landbot ID format: {landbot_id_str}")
        raise HTTPException(status_code=400, detail="Invalid Landbot ID format")
    except Exception as e:
        logger.error(f"Error processing outbound webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
