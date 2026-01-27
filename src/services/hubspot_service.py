from typing import Optional
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInputForCreate as ContactInput, PublicObjectSearchRequest as ContactSearchRequest
from src.config import settings
import requests
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class HubSpotService:
    def __init__(self):
        self._access_token = None
        self._token_expires_at = datetime.min
        # Initialize client without token initially, or with a dummy one
        self.client = HubSpot()

    def _refresh_access_token(self) -> str:
        """
        Refresh the OAuth Access Token using the Refresh Token.
        """
        logger.info("Refreshing HubSpot Access Token...")
        url = "https://api.hubapi.com/oauth/v1/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": settings.HUBSPOT_CLIENT_ID,
            "client_secret": settings.HUBSPOT_CLIENT_SECRET,
            "refresh_token": settings.HUBSPOT_REFRESH_TOKEN
        }
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            tokens = response.json()
            
            self._access_token = tokens["access_token"]
            expires_in = tokens.get("expires_in", 1800)
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60) # Buffer
            
            # Update client with new token
            self.client.access_token = self._access_token
            
            logger.info("Access Token refreshed successfully.")
            return self._access_token
        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            raise e

    def get_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.
        """
        if not self._access_token or datetime.now() >= self._token_expires_at:
            return self._refresh_access_token()
        return self._access_token

    def get_or_create_contact(self, name: str, phone: str) -> str:
        """
        Search for contact by phone. If not found, create one.
        Returns Contact ID.
        """
        # Ensure token is valid
        self.get_token()
        
        # 1. Search by Phone
        filter_group = {
            "filters": [{
                "propertyName": "phone",
                "operator": "EQ",
                "value": phone
            }]
        }
        search_req = ContactSearchRequest(filter_groups=[filter_group], properties=["firstname", "phone"])
        
        try:
            search_res = self.client.crm.contacts.search_api.do_search(public_object_search_request=search_req)
            if search_res.results:
                return search_res.results[0].id
            
            # 2. Create if not found
            properties = {
                "firstname": name,
                "phone": phone
            }
            contact_input = ContactInput(properties=properties)
            create_res = self.client.crm.contacts.basic_api.create(simple_public_object_input_for_create=contact_input)
            return create_res.id
            
        except Exception as e:
            logger.error(f"Error in get_or_create_contact: {e}")
            raise e

    def publish_message_to_channel(self, landbot_id: int, message_text: str, sender_name: str = "Visitor"):
        """
        Publish a message to the HubSpot Custom Channel.
        Identifies the conversation thread by landbot_id.
        """
        token = self.get_token()
        
        url = f"https://api.hubapi.com/conversations/v3/custom-channels/{settings.HUBSPOT_CHANNEL_ID}/messages"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Payload for 'INCOMING' message (Visitor -> HubSpot)
        payload = {
            "text": message_text,
            "channelAccountId": settings.HUBSPOT_CHANNEL_ACCOUNT_ID,
            "integrationThreadId": str(landbot_id),
            "messageDirection": "INCOMING",
            "senders": [
                {
                    "name": sender_name,
                    "deliveryIdentifier": {
                        "type": "CHANNEL_SPECIFIC_OPAQUE_ID",
                        "value": str(landbot_id)
                    }
                }
            ]
        }
        
        logger.info(f"Publishing message to HubSpot: {json.dumps(payload)}")
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            logger.info("Message published successfully.")
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Error publishing message: {e.response.text}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error publishing message: {e}")
            raise e

hubspot_service = HubSpotService()
