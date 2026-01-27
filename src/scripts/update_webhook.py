import requests
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def update_webhook(new_url=None):
    print("=== HubSpot Custom Channel Webhook Updater ===")
    
    developer_api_key = os.getenv("HUBSPOT_DEVELOPER_API_KEY")
    channel_id = os.getenv("HUBSPOT_CHANNEL_ID")
    app_id = os.getenv("HUBSPOT_APP_ID")

    if not developer_api_key:
        print("Error: HUBSPOT_DEVELOPER_API_KEY not found in .env")
        return

    if not channel_id:
        # Fallback: Ask user if not in env
        channel_id = input("Enter HubSpot Channel ID: ").strip()
        if not channel_id:
             print("Error: Channel ID is required.")
             return

    if not new_url:
        if len(sys.argv) > 1:
            new_url = sys.argv[1]
        else:
            new_url = input("Enter the new Webhook URL (e.g. https://xxxx.loca.lt/webhook/hubspot-outbound): ").strip()
    
    if not new_url:
        print("Error: Webhook URL is required.")
        return

    # HubSpot API Endpoint for Custom Channels (requires Developer API Key)
    # PATCH https://api.hubapi.com/conversations/v3/custom-channels/{channelId}
    # Query params: hapikey, appId
    
    url = f"https://api.hubapi.com/conversations/v3/custom-channels/{channel_id}"
    params = {
        "hapikey": developer_api_key,
        "appId": app_id
    }
    
    payload = {
        "webhookUrl": new_url
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Updating Channel {channel_id} with Webhook URL: {new_url}...")
    
    try:
        response = requests.patch(url, params=params, headers=headers, json=payload)
        
        if response.status_code == 200:
            print("✅ Success! Webhook URL updated.")
            print("New Configuration:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Error updating channel: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Exception occurred: {e}")

import json

if __name__ == "__main__":
    update_webhook()
