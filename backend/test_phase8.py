import unittest
import asyncio
import time
import json
from backend.database import init_db, get_connection
from backend.escala import escala

class TestEscalaProtocol(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    async def _async_test_hitl_flow(self):
        # 1. Operation: Bulk Delete (High Risk)
        op_type = "bulk_delete"
        context = {"user": "admin", "target": "all_leads"}
        
        # 2. Check Risk (should return False and create escalation)
        is_safe = escala.check_risk(op_type, context)
        self.assertFalse(is_safe)
        
        # 3. Verify DB Entry is 'pending'
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id, status, context_json FROM escalations WHERE operation_type = ? ORDER BY timestamp DESC LIMIT 1", (op_type,))
        row = c.fetchone()
        self.assertIsNotNone(row)
        req_id = row[0]
        self.assertEqual(row[1], "pending")
        
        ctx_data = json.loads(row[2])
        self.assertIn("Critical operation attempted", ctx_data["reason"])
        
        # 4. Simulate Approval (Like clicking 'Approve' in Reflex UI)
        c.execute("UPDATE escalations SET status = ?, approved_by = ? WHERE id = ?", ("approved", "tester", req_id))
        conn.commit()
        
        # 5. Check status again
        c.execute("SELECT status FROM escalations WHERE id = ?", (req_id,))
        final_status = c.fetchone()[0]
        self.assertEqual(final_status, "approved")
        conn.close()

    def test_escala_lifecycle(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._async_test_hitl_flow())
        loop.close()

if __name__ == "__main__":
    unittest.main()
