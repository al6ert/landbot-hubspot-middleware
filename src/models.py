from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class LandbotCustomer(BaseModel):
    id: int
    name: str
    phone: Optional[str] = None
    
class LandbotMessage(BaseModel):
    customer: LandbotCustomer
    message: str
    timestamp: Optional[int] = None

class HubSpotWebhookPayload(BaseModel):
    # Depending on how the workflow webhook is configured, payload varies.
    # We expect custom payload as defined in implementation plan.
    ticket_id: int
    landbot_id: str
    reply_text: str
