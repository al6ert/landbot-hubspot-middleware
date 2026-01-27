from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from src.config import settings
from src.models import LandbotMessage, HubSpotWebhookPayload
from src.services.hubspot_service import hubspot_service
from src.services.landbot_service import landbot_service
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Landbot-HubSpot Middleware")

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}

@app.post("/webhook/landbot-inbound")
async def landbot_inbound(payload: LandbotMessage, background_tasks: BackgroundTasks):
    """
    Handle incoming messages from Landbot (Human Takeover).
    """
    logger.info(f"Received Landbot payload: {payload.dict()}")
    
    customer_id = payload.customer.id
    customer_name = payload.customer.name
    message_text = payload.message
    
    # 1. Ensure Contact Exists in CRM (Best Practice)
    # This helps HubSpot eventually link the conversation to a real contact
    # if the system logic allows specific matching.
    contact_id = None
    if payload.customer.phone:
        try:
            contact_id = hubspot_service.get_or_create_contact(customer_name, payload.customer.phone)
            logger.info(f"Resolved Contact ID: {contact_id}")
        except Exception as e:
            logger.error(f"Failed to resolve contact: {e}")

    # 2. Publish Message to Custom Channel
    # We use customer_id as the integrationThreadId
    background_tasks.add_task(
        hubspot_service.publish_message_to_channel,
        customer_id,
        message_text,
        sender_name=customer_name
    )
    
    return {"status": "published", "thread_id": str(customer_id)}

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

    # Extract Landbot ID from Thread ID
    if not payload.channelIntegrationThreadIds:
        logger.warning("No channelIntegrationThreadIds found in payload.")
        # Fallback: check nested message integrationThreadId if available (depends on schema version)
        # But per our model, we look at the top level list.
        return {"status": "ignored", "reason": "No thread ID"}

    try:
        # Assuming the first thread ID is the Landbot Customer ID
        landbot_id_str = payload.channelIntegrationThreadIds[0]
        landbot_id = int(landbot_id_str)
        
        message_text = payload.message.text
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
