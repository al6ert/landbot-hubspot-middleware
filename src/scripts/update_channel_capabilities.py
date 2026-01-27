import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

def update_channel():
    developer_api_key = os.getenv("HUBSPOT_DEVELOPER_API_KEY")
    app_id = os.getenv("HUBSPOT_APP_ID")
    channel_id = os.getenv("HUBSPOT_CHANNEL_ID") or "2300310"
    
    if not developer_api_key or not app_id:
        print("Error: HUBSPOT_DEVELOPER_API_KEY and HUBSPOT_APP_ID required in .env")
        return

    print(f"Updating channel {channel_id} with phone number support...")
    
    url = f"https://api.hubapi.com/conversations/v3/custom-channels/{channel_id}?hapikey={developer_api_key}&appId={app_id}"
    
    # We want to keep everything else the same but add HS_PHONE_NUMBER
    payload = {
        "capabilities": {
            "deliveryIdentifierTypes": ["CHANNEL_SPECIFIC_OPAQUE_ID", "HS_PHONE_NUMBER"],
            "richText": ["HYPERLINK", "TEXT_ALIGNMENT", "BLOCKQUOTE"],
            "allowInlineImages": True,
            "allowOutgoingMessages": True,
            "outgoingAttachmentTypes": ["FILE"],
            "threadingModel": "INTEGRATION_THREAD_ID"
        }
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.patch(url, headers=headers, json=payload)
        if response.status_code in [200, 204]:
            print("✅ Channel updated successfully!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Error updating channel: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    update_channel()
