import os
import webbrowser
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# Load env but prioritize manual input for missing values
load_dotenv()

CLIENT_ID = os.getenv("HUBSPOT_CLIENT_ID")
CLIENT_SECRET = os.getenv("HUBSPOT_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/oauth-callback"
SCOPES = "conversations.custom_channels.read conversations.custom_channels.write conversations.read conversations.write conversations.visitor_identification.tokens.create crm.objects.contacts.read crm.objects.contacts.write"

authorization_code = None

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global authorization_code
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        if "code" in params:
            authorization_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Authorization Success!</h1><p>You can close this tab and return to the terminal.</p>")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Authorization Failed. No code received.")

def start_server():
    server = HTTPServer(('localhost', 8000), OAuthHandler)
    # Handle only one request then stop
    server.handle_request()

def main():
    global CLIENT_ID, CLIENT_SECRET
    
    print("=== HubSpot OAuth Setup ===")
    
    if not CLIENT_ID:
        CLIENT_ID = input("Enter HubSpot Client ID: ").strip()
    
    if not CLIENT_SECRET:
        CLIENT_SECRET = input("Enter HubSpot Client Secret: ").strip()
        
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: Client ID and Secret are required.")
        return

    # 1. Generate Auth URL
    auth_url = (
        f"https://app.hubspot.com/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&scope={SCOPES}"
        f"&redirect_uri={REDIRECT_URI}"
    )
    
    print(f"\nOpening browser for authorization...\nURL: {auth_url}")
    webbrowser.open(auth_url)
    
    # 2. Start Local Server to catch Callback
    print("\nWaiting for callback on http://localhost:8000/oauth-callback ...")
    start_server()
    
    if not authorization_code:
        print("Error: Failed to get authorization code.")
        return
        
    print(f"\nAuthorization Code received!")
    
    # 3. Exchange Code for Tokens
    print("Exchanging code for tokens...")
    token_url = "https://api.hubapi.com/oauth/v1/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": authorization_code
    }
    
    response = requests.post(token_url, data=data)
    
    if response.status_code == 200:
        tokens = response.json()
        refresh_token = tokens.get("refresh_token")
        access_token = tokens.get("access_token")
        
        print("\n=== OAUTH SUCCESS ===")
        print(f"REFRESH_TOKEN: {refresh_token}")
        print("\nPlease update your .env file with this token:")
        print(f"HUBSPOT_REFRESH_TOKEN={refresh_token}")
        print("=====================")
    else:
        print(f"\nError exchanging token: {response.text}")

if __name__ == "__main__":
    main()
