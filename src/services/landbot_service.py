import requests
import logging
from src.config import settings

logger = logging.getLogger(__name__)

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
        # Ensure correct URL format with trailing slash
        url = f"https://api.landbot.io/v1/customers/{landbot_id}/send_text/"
        payload = {
            "message": message,
            "extra": {
                "sender": "agent"
            }
        }
        
        logger.info(f"Sending message to Landbot ({landbot_id}): {message}")
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            if response.status_code >= 400:
                logger.error(f"❌ Landbot API Error ({response.status_code}): {response.text}")
            response.raise_for_status()
            res_data = response.json()
            logger.info(f"Message sent to Landbot successfully. Response: {res_data}")
            return res_data
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send message to Landbot: {e}")
            raise e

landbot_service = LandbotService()
