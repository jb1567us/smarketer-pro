import unittest
import asyncio
import json
from backend.database import init_db, get_connection
from backend.agents.visual_agent import visual_agent

class TestOutreachOptimizer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    async def _async_test_carousel_generation(self):
        # 1. Mock Data
        lead_data = {
            "id": 999,
            "name": "Acme Corp",
            "niche": "Advanced Robotics",
            "reputation_score": 95
        }
        
        # 2. Generate Layout
        layout = await visual_agent.generate_carousel_layout(lead_data)
        
        # 3. Verify Structure
        self.assertIsInstance(layout, list)
        self.assertGreater(len(layout), 0)
        self.assertIn("title", layout[0])
        self.assertIn("hex_color", layout[0])
        
        # 4. Mock DB Persistence (verify schema compatibility)
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO content_assets (lead_id, asset_type, layout_json, status, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (lead_data["id"], "carousel", json.dumps(layout), "draft", 123456789))
        conn.commit()
        
        # 5. Verify Retrieval
        c.execute("SELECT layout_json FROM content_assets WHERE lead_id = 999")
        row = c.fetchone()
        self.assertIsNotNone(row)
        retrieved_layout = json.loads(row[0])
        self.assertEqual(len(retrieved_layout), len(layout))
        
        conn.close()

    def test_visual_logic(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._async_test_carousel_generation())
        loop.close()

if __name__ == "__main__":
    unittest.main()
