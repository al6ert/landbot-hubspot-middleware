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

class DeliveryIdentifier(BaseModel):
    type: str
    value: str

class HubSpotParticipant(BaseModel):
    name: Optional[str] = None
    deliveryIdentifier: Optional[DeliveryIdentifier] = None
    actorId: Optional[str] = None

class HubSpotMessageContent(BaseModel):
    text: Optional[str] = None
    richText: Optional[str] = None

class HubSpotWebhookPayload(BaseModel):
    type: str
    channelId: str
    message: HubSpotMessageContent
    channelIntegrationThreadIds: list[str] = []
    recipients: list[HubSpotParticipant] = []
    senders: list[HubSpotParticipant] = []
    
    # Allow extra fields safely
    model_config = {"extra": "ignore"}
