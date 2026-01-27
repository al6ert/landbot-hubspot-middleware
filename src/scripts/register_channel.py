import requests
import json
import os
from dotenv import load_dotenv

# Try to load from .env, but prioritize user input if needed
load_dotenv()

def get_access_token():
    """Helper to get fresh access token using refresh token"""
    refresh_token = os.getenv("HUBSPOT_REFRESH_TOKEN")
    client_id = os.getenv("HUBSPOT_CLIENT_ID")
    client_secret = os.getenv("HUBSPOT_CLIENT_SECRET")
    
    if not refresh_token:
        return None
        
    url = "https://api.hubapi.com/oauth/v1/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token
    }
    try:
        res = requests.post(url, data=data)
        if res.status_code == 200:
            return res.json().get("access_token")
        else:
            print(f"Error refreshing token: {res.text}")
            return None
    except Exception as e:
        print(f"Error requesting token: {e}")
        return None

def register_channel():
    print("=== HubSpot Custom Channel Registration (Public App) ===")
    
    developer_api_key = os.getenv("HUBSPOT_DEVELOPER_API_KEY")
    app_id = os.getenv("HUBSPOT_APP_ID")
    
    if not developer_api_key:
        developer_api_key = input("Enter HubSpot Developer API Key: ").strip()
    
    if not app_id:
        app_id = input("Enter HubSpot App ID: ").strip()

    # Get Access Token for Step 2
    access_token = get_access_token()
    if not access_token:
        print("Error: Could not obtain Access Token. Ensure HUBSPOT_REFRESH_TOKEN is in .env")
        # Allow manual entry for fallback
        access_token = input("Or enter a valid Access Token manually: ").strip()

    if not access_token:
        print("Aborting. Valid Access Token required for Step 2.")
        return

    webhook_url = input("Enter your Webhook URL (e.g., https://your-server.com/webhook/hubspot-outbound): ").strip()
    
    channel_id = input("\nEnter Channel ID if already created (leave blank to create new): ").strip()
    
    if not channel_id:
        # 1. Create Custom Channel Definition (Requires Developer API Key)
        print("\n[1/3] Creating Custom Channel Definition...")
        
        channel_url = f"https://api.hubapi.com/conversations/v3/custom-channels?hapikey={developer_api_key}"
        channel_url += f"&appId={app_id}"
        
        channel_payload = {
            "name": "Landbot Integration",
            "webhookUrl": webhook_url,
            "capabilities": {
                "deliveryIdentifierTypes": ["CHANNEL_SPECIFIC_OPAQUE_ID"], 
                "richText": ["HYPERLINK", "TEXT_ALIGNMENT", "BLOCKQUOTE"],
                "allowInlineImages": True,
                "allowOutgoingMessages": True,
                "outgoingAttachmentTypes": ["FILE"],
                "threadingModel": "INTEGRATION_THREAD_ID"
            },
            "channelDescription": "Channel for Landbot conversations",
            "channelAccountConnectionRedirectUrl": "https://landbot.io" 
        }
        
        headers_dev = {"Content-Type": "application/json"}
        response = requests.post(channel_url, headers=headers_dev, json=channel_payload)
        
        if response.status_code in [200, 201]:
            channel_data = response.json()
            channel_id = channel_data["id"]
            print(f"Success! Channel ID: {channel_id}")
        else:
            print(f"Error creating channel: {response.text}")
            channel_id = input("If channel already exists, enter Channel ID manually (or press Enter to abort): ").strip()

    if not channel_id:
        return

    # 2. Fetch Inboxes (to get a valid inboxId)
    print("\n[2/3] Fetching available Inboxes...")
    inbox_url = "https://api.hubapi.com/conversations/v3/conversations/inboxes"
    headers_oauth = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    res_inboxes = requests.get(inbox_url, headers=headers_oauth)
    inbox_id = None
    if res_inboxes.status_code == 200:
        inboxes = res_inboxes.json().get("results", [])
        if not inboxes:
            print("Error: No inboxes found in this HubSpot account. Please create an Inbox first.")
            return
        
        print("Available Inboxes:")
        for i, ib in enumerate(inboxes):
            print(f"{i}: {ib.get('name')} (ID: {ib.get('id')})")
        
        choice = input("\nSelect the index of the inbox to use (default 0): ").strip()
        idx = int(choice) if choice.isdigit() and int(choice) < len(inboxes) else 0
        inbox_id = inboxes[idx]["id"]
        print(f"Using Inbox: {inboxes[idx].get('name')} ({inbox_id})")
    else:
        print(f"Error fetching inboxes: {res_inboxes.text}")
        inbox_id = input("Please enter an Inbox ID manually: ").strip()

    if not inbox_id:
        print("Aborting. Inbox ID is required.")
        return

    # 3. Connect Channel Account (Requires OAuth Access Token)
    print("\n[3/3] Connecting Channel Account...")
    account_url = f"https://api.hubapi.com/conversations/v3/custom-channels/{channel_id}/channel-accounts"
    
    account_payload = {
        "name": "Landbot Bot",
        "accountId": "landbot-bot-01",
        "inboxId": inbox_id,
        "deliveryIdentifier": {
            "type": "CHANNEL_SPECIFIC_OPAQUE_ID",
            "value": "landbot-default-id"
        }
    }
    
    response_account = requests.post(account_url, headers=headers_oauth, json=account_payload)
    
    if response_account.status_code not in [200, 201]:
        print(f"Error connecting account: {response_account.text}")
        print(f"Your Channel ID is: {channel_id}")
        return

    account_data = response_account.json()
    account_id = account_data["id"]
    print(f"Success! Channel Account ID: {account_id}")
    
    print("\n=== REGISTRATION COMPLETE ===")
    print("Please add these lines to your .env file:")
    print(f"HUBSPOT_CHANNEL_ID={channel_id}")
    print(f"HUBSPOT_CHANNEL_ACCOUNT_ID={account_id}")
    print("=============================")

if __name__ == "__main__":
    register_channel()
