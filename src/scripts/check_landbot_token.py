import requests
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

def check_token():
    load_dotenv()
    token = os.getenv("LANDBOT_API_TOKEN")
    url = "https://api.landbot.io/v1/projects/"
    headers = {"Authorization": f"Token {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Token is valid.")
            data = response.json()
            print(f"Projects found: {len(data.get('results', []))}")
            for p in data.get('results', []):
                print(f"- {p.get('name')} (ID: {p.get('id')})")
        else:
            print(f"❌ Token invalid or error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_token()
