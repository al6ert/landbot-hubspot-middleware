import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.config import settings
from src.services.hubspot_service import hubspot_service

def test_hubspot_contact(name, phone, landbot_id):
    print(f"Testing contact creation/search in HubSpot for {name} ({landbot_id})...")
    try:
        contact_id = hubspot_service.get_or_create_contact(name, phone, landbot_id=str(landbot_id))
        print(f"✅ Contact ID: {contact_id}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    load_dotenv()
    test_hubspot_contact("Test User", None, "9999999")
