import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    HUBSPOT_ACCESS_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN", "")
    LANDBOT_API_TOKEN = os.getenv("LANDBOT_API_TOKEN", "")
    
    # Custom Property Internal Names (Must match HubSpot exactly)
    PROP_LANDBOT_ID = "landbot_customer_id"
    PROP_WHATSAPP_REPLY = "whatsapp_reply_body"

settings = Settings()
