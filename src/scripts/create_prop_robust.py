import requests
import os
import sys
import json
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.config import settings
from src.services.hubspot_service import hubspot_service

def create_property():
    load_dotenv()
    print("Refreshing token...")
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
    
    print(f"Creating property '{settings.PROP_LANDBOT_ID}' with payload: {json.dumps(payload)}")
    response = requests.post(url, headers=headers, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Body: {response.text}")

if __name__ == "__main__":
    create_property()
