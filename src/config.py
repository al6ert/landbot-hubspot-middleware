import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class Settings:
    LANDBOT_API_TOKEN = os.getenv("LANDBOT_API_TOKEN", "")
    
    # OAuth Credentials
    HUBSPOT_CLIENT_ID = os.getenv("HUBSPOT_CLIENT_ID", "")
    HUBSPOT_CLIENT_SECRET = os.getenv("HUBSPOT_CLIENT_SECRET", "")
    HUBSPOT_REFRESH_TOKEN = os.getenv("HUBSPOT_REFRESH_TOKEN", "")
    
    # Developer Credentials (for Channel Registration)
    HUBSPOT_DEVELOPER_API_KEY = os.getenv("HUBSPOT_DEVELOPER_API_KEY", "")
    HUBSPOT_APP_ID = os.getenv("HUBSPOT_APP_ID", "")
    
    # Custom Channels Config
    HUBSPOT_CHANNEL_ID = os.getenv("HUBSPOT_CHANNEL_ID", "")
    HUBSPOT_CHANNEL_ACCOUNT_ID = os.getenv("HUBSPOT_CHANNEL_ACCOUNT_ID", "")
    
    # Custom Property Internal Names
    PROP_LANDBOT_ID = "landbot_customer_id"

    @classmethod
    def validate(cls):
        missing = []
        if not cls.HUBSPOT_CHANNEL_ID: missing.append("HUBSPOT_CHANNEL_ID")
        if not cls.HUBSPOT_CHANNEL_ACCOUNT_ID: missing.append("HUBSPOT_CHANNEL_ACCOUNT_ID")
        
        if missing:
            print(f"⚠️  WARNING: Missing configuration in .env: {', '.join(missing)}")
        else:
            print(f"✅ Configuration loaded: Channel ID {cls.HUBSPOT_CHANNEL_ID}")

settings = Settings()
settings.validate()
