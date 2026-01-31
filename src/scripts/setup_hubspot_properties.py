import requests
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.config import settings
from src.services.hubspot_service import hubspot_service

def create_landbot_id_property():
    print(f"Creating property '{settings.PROP_LANDBOT_ID}' in HubSpot...")
    
    token = hubspot_service.get_token()
    url = "https://api.hubapi.com/crm/v3/properties/contacts"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "name": settings.PROP_LANDBOT_ID,
        "label": "Landbot Customer ID",
        "type": "string",
        "fieldType": "text",
        "groupName": "contactinformation",
        "hasUniqueValue": False,
        "hidden": False,
        "formField": True,
        "displayOrder": -1
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201:
            print(f"✅ Property '{settings.PROP_LANDBOT_ID}' created successfully.")
        elif response.status_code == 409:
            print(f"ℹ️  Property '{settings.PROP_LANDBOT_ID}' already exists.")
        else:
            print(f"❌ Failed to create property: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    load_dotenv()
    create_landbot_id_property()
