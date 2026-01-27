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
    message_text = payload.message
    
    # Logic: Check if there is an active ticket
    active_ticket_id = hubspot_service.find_active_ticket(customer_id)
    
    if active_ticket_id:
        logger.info(f"Found active ticket {active_ticket_id} for user {customer_id}")
        # Add note to existing ticket
        # Run in background to reply fast to Landbot
        background_tasks.add_task(
            hubspot_service.add_note_to_ticket, 
            active_ticket_id, 
            message_text, 
            "Inbound"
        )
        return {"status": "merged", "ticket_id": active_ticket_id}
    else:
        logger.info(f"No active ticket for user {customer_id}. Creating new one.")
        # Create new ticket
        new_ticket_id = hubspot_service.create_ticket(
            payload.customer.dict(), 
            message_text
        )
        # Also add the first message as a note for consistency
        background_tasks.add_task(
            hubspot_service.add_note_to_ticket,
            new_ticket_id,
            message_text,
            "Inbound"
        )
        return {"status": "created", "ticket_id": new_ticket_id}

@app.post("/webhook/hubspot-outbound")
async def hubspot_outbound(payload: HubSpotWebhookPayload, background_tasks: BackgroundTasks):
    """
    Handle outgoing messages from HubSpot Agent (via Workflow).
    """
    logger.info(f"Received HubSpot payload: {payload.dict()}")
    
    # Logic: Send message to Landbot
    try:
        # Convert landbot_id to int as required by Landbot API
        landbot_id_int = int(payload.landbot_id)
        
        background_tasks.add_task(
            landbot_service.send_text_message,
            landbot_id_int,
            payload.reply_text
        )
        
        # Optional: Add the agent reply as a note to the ticket for record keeping (if HubSpot doesn't do it automatically)
        background_tasks.add_task(
            hubspot_service.add_note_to_ticket,
            str(payload.ticket_id),
            payload.reply_text,
            "Outbound"
        )
        
        return {"status": "sent"}
        
    except ValueError:
        logger.error(f"Invalid Landbot ID: {payload.landbot_id}")
        raise HTTPException(status_code=400, detail="Invalid Landbot ID")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
