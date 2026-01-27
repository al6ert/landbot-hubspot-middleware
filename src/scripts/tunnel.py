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
            print(f"🔄 Updating HubSpot with: {webhook_url}")
            
            # Execute the update script
            update_cmd = [sys.executable, 'src/scripts/update_webhook.py', webhook_url]
            try:
                # Run the update script as a subprocess
                result = subprocess.run(update_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ HubSpot updated successfully!")
                else:
                    print(f"❌ Error updating HubSpot:\n{result.stderr}")
            except Exception as e:
                print(f"❌ Failed to run update script: {e}")
            
            print("\n🚀 Tunnel is LIVE. Keep this process running.")
            print(f"📢 IMPORTANT: Update Landbot Webhook to: {url}/webhook/landbot-inbound\n")
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
