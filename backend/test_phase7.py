import unittest
import asyncio
import time
from backend.database import init_db, get_connection
from backend.crm_manager import CRMManager, WebhookManager

class TestAutoPilotCRM(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    async def _async_test_sync(self):
        crm = CRMManager()
        webhook = WebhookManager()
        
        # 1. Setup Mock Lead
        lead_id = 999
        lead_data = {"id": lead_id, "name": "CRM Test Lead", "reputation_score": 98}
        
        # 2. Test CRM Sync
        ext_id = await crm.sync_lead(lead_data)
        self.assertTrue(ext_id.startswith("hs_"))
        
        # 3. Test Webhook Trigger
        success = await webhook.trigger_notification("test_event", lead_data)
        self.assertTrue(success)
        
        # 4. Verify DB Logs
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT provider, status FROM crm_sync_log WHERE lead_id = ? ORDER BY timestamp DESC LIMIT 1", (lead_id,))
        row = c.fetchone()
        conn.close()
        
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "HubSpot")
        self.assertEqual(row[1], "success")

    def test_crm_lifecycle(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._async_test_sync())
        loop.close()

if __name__ == "__main__":
    unittest.main()
