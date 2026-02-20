import reflex as rx
import asyncio
import time
from typing import List, Dict, Any
from .base import BaseState
from backend.database import get_connection
from backend.crm_manager import crm_manager, webhook_manager

class CRMState(BaseState):
    """Reflex state for Phase 7: AutoPilot CRM."""
    
    hubspot_api_key: str = "••••••••••••••••"
    zapier_webhook_url: str = "https://hooks.zapier.com/v1/event/mock"
    auto_sync_enabled: bool = True
    
    sync_logs: List[Dict[str, Any]] = []
    is_syncing: bool = False
    
    async def poll_crm_logs(self):
        """Update CRM sync logs from DB."""
        while True:
            try:
                conn = get_connection()
                c = conn.cursor()
                c.execute('''
                    SELECT l.id, p.name, l.provider, l.status, l.timestamp 
                    FROM crm_sync_log l
                    JOIN company_profiles p ON l.lead_id = p.id
                    ORDER BY l.timestamp DESC LIMIT 10
                ''')
                self.sync_logs = [
                    {
                        "id": r[0],
                        "name": r[1],
                        "provider": r[2],
                        "status": r[3],
                        "ts": r[4]
                    } for r in c.fetchall()
                ]
                conn.close()
            except Exception as e:
                print(f"CRM polling error: {e}")
            
            await asyncio.sleep(5)

    async def sync_individual_lead(self, lead_data: Dict[str, Any]):
        """Manually trigger sync for a specific lead."""
        self.is_syncing = True
        self.add_log(f"🔄 Syncing {lead_data.get('name')} to HubSpot CRM...")
        yield
        
        try:
            # 1. Sync to CRM
            ext_id = await crm_manager.sync_lead(lead_data)
            
            # 2. Trigger Webhook (Zapier notification)
            await webhook_manager.trigger_notification("lead_synced", {
                "name": lead_data.get("name"),
                "hubspot_id": ext_id,
                "score": lead_data.get("reputation_score")
            })
            
            self.add_log(f"✅ CRM: {lead_data.get('name')} successfully linked (ID: {ext_id})")
        except Exception as e:
            self.add_log(f"❌ CRM Sync Error: {e}")
            
        self.is_syncing = False
        yield

    def toggle_auto_sync(self):
        self.auto_sync_enabled = not self.auto_sync_enabled
        self.add_log(f"CRM Policy: Auto-Sync set to {self.auto_sync_enabled}")
