import requests
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.config import settings

def test_landbot_message(customer_id, message):
    url = f"https://api.landbot.io/v1/customers/{customer_id}/send_text/"
    headers = {
        "Authorization": f"Token {settings.LANDBOT_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "message": message,
        "extra": {
            "sender": "agent"
        }
    }
    
    print(f"Sending test message to Landbot customer {customer_id}...")
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    load_dotenv()
    if len(sys.argv) < 3:
        print("Usage: python src/scripts/test_landbot_message.py <customer_id> <message>")
    else:
        test_landbot_message(sys.argv[1], sys.argv[2])
