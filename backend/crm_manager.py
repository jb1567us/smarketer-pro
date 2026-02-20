import logging
import time
import requests
from typing import Dict, Any, Optional
from backend.database import get_connection

logger = logging.getLogger(__name__)

class CRMManager:
    """
    Handles synchronization of leads to HubSpot CRM.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or "MOCK_HUBSPOT_KEY_12345"
        self.base_url = "https://api.hubapi.com/crm/v3/objects/contacts"

    async def sync_lead(self, lead_data: Dict[str, Any]) -> str:
        """
        Create or update a contact in HubSpot.
        Returns the external HubSpot ID.
        """
        lead_id = lead_data.get("id")
        name = lead_data.get("name", "Unknown")
        email = lead_data.get("email", f"info@{name.lower().replace(' ', '')}.com")
        
        logger.info(f"[CRM] Syncing {name} to HubSpot...")
        
        # Simulate API Latency
        import asyncio
        await asyncio.sleep(1)
        
        # In a real implementation, we would use requests or a library like 'hubspot-api-client'
        # For this prototype, we simulate a successful contact creation
        external_id = f"hs_{int(time.time() * 1000)}"
        
        # Log to Sync Table
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO crm_sync_log (lead_id, provider, external_id, status, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (lead_id, "HubSpot", external_id, "success", int(time.time())))
        conn.commit()
        conn.close()
        
        return external_id

class WebhookManager:
    """
    Dispatches payloads to Zapier/Make.com webhooks.
    """
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or "https://hooks.zapier.com/v1/event/mock"

    async def trigger_notification(self, event_type: str, payload: Dict[str, Any]) -> bool:
        """
        Sends a POST request to the configured webhook.
        """
        logger.info(f"[Webhook] Triggering {event_type} notification...")
        
        # Prepare Envelope
        envelope = {
            "event": event_type,
            "timestamp": time.time(),
            "data": payload
        }
        
        try:
            # Simulate Success for prototype
            # In real use: response = requests.post(self.webhook_url, json=envelope)
            # return response.status_code == 200
            return True
        except Exception as e:
            logger.error(f"[Webhook] Dispatch Error: {e}")
            return False

# Global instances (Singletons for State)
crm_manager = CRMManager()
webhook_manager = WebhookManager()
