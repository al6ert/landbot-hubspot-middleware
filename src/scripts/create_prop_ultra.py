import requests
import os
import sys
import json
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Mocking settings and service to avoid imports that might hang
load_dotenv()
CLIENT_ID = os.getenv("HUBSPOT_CLIENT_ID")
CLIENT_SECRET = os.getenv("HUBSPOT_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("HUBSPOT_REFRESH_TOKEN")

def get_token():
    print("Refreshing HubSpot Access Token...")
    url = "https://api.hubapi.com/oauth/v1/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN
    }
    resp = requests.post(url, data=data, timeout=10)
    resp.raise_for_status()
    return resp.json()["access_token"]

def create_property():
    try:
        token = get_token()
        print("Token obtained.")
        
        url = "https://api.hubapi.com/crm/v3/properties/contacts"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "name": "landbot_customer_id",
            "label": "Landbot Customer ID",
            "type": "string",
            "fieldType": "text",
            "groupName": "contactinformation",
            "hasUniqueValue": False,
            "hidden": False,
            "formField": True,
            "displayOrder": -1
        }
        
        print(f"Creating property...")
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Body: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_property()
