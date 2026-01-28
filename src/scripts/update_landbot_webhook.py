import requests
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def update_landbot_webhook(new_url=None):
    print("=== Landbot Message Hook Updater ===")
    
    token = os.getenv("LANDBOT_API_TOKEN")
    channel_id = os.getenv("LANDBOT_CHANNEL_ID")
    
    if not token or not channel_id:
        print("Error: LANDBOT_API_TOKEN or LANDBOT_CHANNEL_ID not found in .env")
        return

    if not new_url:
        if len(sys.argv) > 1:
            new_url = sys.argv[1]
        else:
            new_url = input("Enter the new Landbot Webhook URL (e.g. https://xxxx.loca.lt/webhook/landbot-inbound): ").strip()
    
    if not new_url:
        print("Error: Webhook URL is required.")
        return

    headers = {
        "Authorization": f"Token {token}"
    }

    # 1. Get existing hooks
    try:
        get_url = f"https://api.landbot.io/v1/channels/{channel_id}/message_hooks/"
        print(f"Fetching existing hooks for channel {channel_id}...")
        response = requests.get(get_url, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Error fetching hooks: {response.status_code}")
            print(response.text)
            return

        hooks = response.json().get("hooks", [])
        print(f"Found {len(hooks)} existing hook(s).")
        
        # 2. Delete existing hooks
        for hook in hooks:
            hook_id = hook["id"]
            hook_url = hook.get("url")
            print(f"Deleting existing hook {hook_id} ({hook_url})...")
            
            del_url = f"https://api.landbot.io/v1/channels/{channel_id}/message_hooks/{hook_id}/"
            del_res = requests.delete(del_url, headers=headers)
            
            if del_res.status_code in [200, 204]:
                print(f"✅ Hook {hook_id} deleted.")
            else:
                print(f"❌ Failed to delete hook {hook_id}: {del_res.status_code}")
                print(del_res.text)

        # 3. Create new hook
        # The user specified x-www-form-urlencoded
        print(f"Creating new Landbot hook: {new_url}")
        post_url = f"https://api.landbot.io/v1/channels/{channel_id}/message_hooks/"
        payload = {
            "name": "landbot_hubspot_hook",
            "url": new_url
        }
        
        # Using data= instead of json= sends it as x-www-form-urlencoded
        post_res = requests.post(post_url, headers=headers, data=payload)
        
        if post_res.status_code in [200, 201]:
            print("✅ Landbot webhook updated successfully!")
            print(post_res.json())
        else:
            print(f"❌ Error creating Landbot hook: {post_res.status_code}")
            print(post_res.text)

    except Exception as e:
        print(f"❌ Exception occurred: {e}")

if __name__ == "__main__":
    update_landbot_webhook()
