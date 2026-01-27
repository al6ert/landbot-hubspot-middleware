import requests
import os
from dotenv import load_dotenv

load_dotenv()

def update_channel():
    channel_id = os.getenv("HUBSPOT_CHANNEL_ID")
    dev_key = os.getenv("HUBSPOT_DEVELOPER_API_KEY")
    app_id = os.getenv("HUBSPOT_APP_ID")
    
    if not all([channel_id, dev_key, app_id]):
        print("Missing config")
        return

    url = f"https://api.hubapi.com/conversations/v3/custom-channels/{channel_id}?hapikey={dev_key}&appId={app_id}"
    
    payload = {
        "capabilities": {
            "deliveryIdentifierTypes": ["CHANNEL_SPECIFIC_OPAQUE_ID", "HS_PHONE_NUMBER"],
            "threadingModel": "INTEGRATION_THREAD_ID",
            "allowInlineImages": True,
            "allowOutgoingMessages": True,
            "outgoingAttachmentTypes": ["FILE"],
            "richText": ["HYPERLINK", "TEXT_ALIGNMENT", "BLOCKQUOTE"]
        }
    }
    
    res = requests.patch(url, json=payload)
    if res.status_code == 200:
        import json
        print("Channel updated successfully!")
        print(json.dumps(res.json(), indent=2))
    else:
        print(f"Error: {res.status_code} - {res.text}")

if __name__ == "__main__":
    update_channel()
