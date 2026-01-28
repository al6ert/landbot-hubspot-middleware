import subprocess
import re
import sys
import time
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def get_public_ip():
    try:
        return requests.get('https://api.ipify.org').text
    except:
        return "Unknown"

def run_tunnel():
    print("=== Automating Tunnel & HubSpot Webhook ===")
    
    ip = get_public_ip()
    print(f"📍 Your Public IP is: {ip}")
    print("👉 If localtunnel asks for a password in the browser, use this IP.\n")
    
    # Start localtunnel
    # We use -s to try to get a sub-domain if available, but let's stick to simple port for now
    process = subprocess.Popen(
        ['pnpm', 'dlx', 'localtunnel', '--port', '8000'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    url = None
    print("⏳ Starting tunnel...")
    
    # Wait for the URL to appear in output
    for line in iter(process.stdout.readline, ""):
        print(line.strip())
        match = re.search(r'your url is: (https://[a-z0-9-]+\.loca\.lt)', line)
        if match:
            url = match.group(1)
            webhook_url = f"{url}/webhook/hubspot-outbound"
            print(f"\n✅ Tunnel ready: {url}")
            
            # Execute the HubSpot update script
            hubspot_update_cmd = [sys.executable, 'src/scripts/update_webhook.py', webhook_url]
            try:
                print(f"🔄 Updating HubSpot with: {webhook_url}")
                result = subprocess.run(hubspot_update_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ HubSpot updated successfully!")
                else:
                    print(f"❌ Error updating HubSpot:\n{result.stderr}")
            except Exception as e:
                print(f"❌ Failed to run HubSpot update script: {e}")

            # Execute the Landbot update script
            landbot_webhook_url = f"{url}/webhook/landbot-inbound"
            landbot_update_cmd = [sys.executable, 'src/scripts/update_landbot_webhook.py', landbot_webhook_url]
            try:
                print(f"🔄 Updating Landbot with: {landbot_webhook_url}")
                result = subprocess.run(landbot_update_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ Landbot updated successfully!")
                else:
                    print(f"❌ Error updating Landbot:\n{result.stderr}")
            except Exception as e:
                print(f"❌ Failed to run Landbot update script: {e}")
            
            print("\n🚀 Tunnel is LIVE and Webhooks are registered. Keep this process running.")
            break

    # Keep reading output to prevent buffer filled and keep process alive
    try:
        for line in iter(process.stdout.readline, ""):
            if line:
                # Silently consume or print if you prefer
                pass
    except KeyboardInterrupt:
        print("\n👋 Stopping tunnel...")
        process.terminate()

if __name__ == "__main__":
    try:
        run_tunnel()
    except KeyboardInterrupt:
        sys.exit(0)
