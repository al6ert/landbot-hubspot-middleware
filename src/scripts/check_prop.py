import requests
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.services.hubspot_service import hubspot_service

def check_property():
    load_dotenv()
    token = hubspot_service.get_token()
    url = "https://api.hubapi.com/crm/v3/properties/contacts/landbot_customer_id"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Body: {response.text}")

if __name__ == "__main__":
    check_property()
