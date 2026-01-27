import requests
from src.config import settings

class LandbotService:
    def __init__(self):
        self.base_url = "https://api.landbot.io/v1"
        self.headers = {
            "Authorization": f"Token {settings.LANDBOT_API_TOKEN}",
            "Content-Type": "application/json"
        }

    def send_text_message(self, landbot_id: int, message: str):
        """
        Send a text message to a Landbot user.
        WARNING: For WhatsApp, this only works within the 24h session window.
        """
        url = f"{self.base_url}/customers/{landbot_id}/send_text"
        payload = {
            "message": message,
            "extra": {
                "sender": "agent" # Optional: to mark it differently in Landbot if supported
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error sending message to Landbot: {e}")
            if e.response:
                print(f"Response: {e.response.text}")
            raise e

landbot_service = LandbotService()
