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
            # In MessageHooks: msg_item['sender']['type'] 
            # In Webhook block: might be different
            sender = msg_item.get("sender", {})
            sender_type = sender.get("type") or msg_item.get("author_type")
            
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
            
            # IMPORTANT: We only bridge to HubSpot if an agent is assigned
            # This prevents bot "noise" from filling HubSpot
            if not agent_id:
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
    Logic to ensure contact exists and publish message.
    """
    try:
        # 1. Ensure Contact Exists & Associated
        # By searching/creating with phone, HubSpot Conversations will try to auto-stitch
        if customer_phone:
            try:
                hubspot_service.get_or_create_contact(customer_name, customer_phone)
            except Exception as e:
                logger.error(f"Failed to sync contact to HubSpot: {e}")

        # 2. Publish Message
        hubspot_service.publish_message_to_channel(
            customer_id,
            message_text,
            sender_name=customer_name,
            phone=customer_phone
        )
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
    if payload.channelIntegrationThreadIds:
        landbot_id_str = payload.channelIntegrationThreadIds[0]
    
    # Optional: HubSpot also sends recipients in some payload versions
    # For now, we expect the Thread ID to match our Landbot Customer ID
    
    if not landbot_id_str:
        logger.warning(f"No thread ID found in payload: {payload.dict()}")
        return {"status": "ignored", "reason": "No thread ID"}

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
        logger.error(f"Invalid Landbot ID format in thread ID: {payload.channelIntegrationThreadIds}")
        raise HTTPException(status_code=400, detail="Invalid Thread ID format")
    except Exception as e:
        logger.error(f"Error processing outbound webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
