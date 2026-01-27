from typing import Optional
from hubspot import HubSpot
from hubspot.crm.tickets import SimplePublicObjectInputForCreate, PublicObjectSearchRequest
from hubspot.crm.contacts import SimplePublicObjectInputForCreate as ContactInput, PublicObjectSearchRequest as ContactSearchRequest
from hubspot.crm.objects.notes import SimplePublicObjectInputForCreate as NoteInput
from src.config import settings
import json
from datetime import datetime

class HubSpotService:
    def __init__(self):
        self.client = HubSpot(access_token=settings.HUBSPOT_ACCESS_TOKEN)

    def find_active_ticket(self, landbot_id: int) -> Optional[str]:
        """
        Search for an OPEN ticket with the specific landbot_customer_id.
        """
        filter_group = {
            "filters": [
                {
                    "propertyName": settings.PROP_LANDBOT_ID,
                    "operator": "EQ",
                    "value": str(landbot_id)
                },
                {
                    "propertyName": "hs_pipeline_stage",
                    "operator": "NEQ", 
                    "value": "4" # Assuming '4' is Closed. TODO: Verify pipeline stage IDs.
                }
            ]
        }
        
        public_object_search_request = PublicObjectSearchRequest(
            filter_groups=[filter_group],
            properties=["subject", "hs_pipeline_stage", settings.PROP_LANDBOT_ID]
        )
        
        try:
            response = self.client.crm.tickets.search_api.do_search(
                public_object_search_request=public_object_search_request
            )
            if response.results:
                return response.results[0].id
            return None
        except Exception as e:
            print(f"Error searching ticket: {e}")
            return None

    
    def get_or_create_contact(self, name: str, phone: str) -> str:
        """
        Search for contact by phone. If not found, create one.
        Returns Contact ID.
        """
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
            print(f"Error in get_or_create_contact: {e}")
            # Fallback: If we can't create/find contact, we might return None, 
            # but to be safe let's re-raise or handle. 
            # ideally we shouldn't block ticket creation if contact fails, but business logic varies.
            raise e

    def create_ticket(self, customer_data: dict, initial_message: str) -> str:
        """
        Create a new ticket and associate it with the Contact.
        """
        # 1. Provide Contact resolution
        contact_id = None
        if customer_data.get('phone'):
            try:
                contact_id = self.get_or_create_contact(customer_data['name'], customer_data['phone'])
            except Exception as e:
                print(f"Warning: Could not link contact: {e}")

        # 2. Create Ticket
        properties = {
            "subject": f"Chat with {customer_data['name']}",
            "hs_pipeline": "0", 
            "hs_pipeline_stage": "1",
            "hs_ticket_priority": "HIGH",
            settings.PROP_LANDBOT_ID: str(customer_data['id']),
            "content": f"Initial message: {initial_message}" 
        }
        
        ticket_input = SimplePublicObjectInputForCreate(properties=properties)
        try:
            ticket_response = self.client.crm.tickets.basic_api.create(
                simple_public_object_input_for_create=ticket_input
            )
            ticket_id = ticket_response.id
            
            # 3. Associate Ticket with Contact (if found/created)
            if contact_id:
                self.client.crm.associations.v4.basic_api.create(
                    object_type="ticket",
                    object_id=ticket_id,
                    to_object_type="contact",
                    to_object_id=contact_id,
                    association_spec=[
                        {
                            "associationCategory": "HUBSPOT_DEFINED",
                            "associationTypeId": 16 # Ticket to Contact (Standard)
                        }
                    ]
                )
            
            return ticket_id
        except Exception as e:
            print(f"Error creating ticket: {e}")
            raise e

    def add_note_to_ticket(self, ticket_id: str, message: str, direction: str = "Inbound"):
        """
        Create a Note and associate it with the Ticket.
        
        Direction: 'Inbound' (User -> Agent) or 'Outbound' (Agent -> User)
        """
        timestamp = int(datetime.now().timestamp() * 1000)
        
        # Format the note specifically for readability
        note_body = f"<b>[{direction}] from WhatsApp:</b><br/>{message}"
        
        properties = {
            "hs_timestamp": str(timestamp),
            "hs_note_body": note_body
        }
        
        note_input = NoteInput(properties=properties)
        
        try:
            # 1. Create Note
            note_response = self.client.crm.objects.notes.basic_api.create(
                simple_public_object_input_for_create=note_input
            )
            note_id = note_response.id
            
            # 2. Associate Note with Ticket
            # Association Type ID for Note to Ticket is usually 228
            self.client.crm.associations.v4.basic_api.create(
                object_type="note",
                object_id=note_id,
                to_object_type="ticket",
                to_object_id=ticket_id,
                association_spec=[
                    {
                        "associationCategory": "HUBSPOT_DEFINED",
                        "associationTypeId": 228 
                    }
                ]
            )
            return note_id
            
        except Exception as e:
            print(f"Error adding note: {e}")
            raise e

hubspot_service = HubSpotService()
