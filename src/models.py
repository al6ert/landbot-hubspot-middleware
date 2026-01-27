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

class HubSpotMessageContent(BaseModel):
    text: Optional[str] = None
    richText: Optional[str] = None

class HubSpotWebhookPayload(BaseModel):
    type: str
    channelId: str
    message: HubSpotMessageContent
    channelIntegrationThreadIds: list[str] = []
    
    # Allow extra fields safely
    model_config = {"extra": "ignore"}
