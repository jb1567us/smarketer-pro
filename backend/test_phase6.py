import unittest
import asyncio
import time
from backend.database import init_db, get_connection
from b2b_outreach_proto.states.video import VideoState
from backend.agents.video_agent import VideoAgent

class TestVideoLab(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    async def _async_test_flow(self):
        # 1. Setup Mock Lead
        lead_data = {"id": 1, "name": "Test Lead", "niche": "Software", "city": "Austin", "reputation_score": 95}
        
        # 2. Test Agent Script Generation
        agent = VideoAgent()
        script = await agent.generate_script(lead_data)
        self.assertTrue("[Speak:" in script)
        
        # 3. Test Manual DB Entry (Simulate state behavior)
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO video_jobs (lead_id, lead_name, script, status, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (lead_data["id"], lead_data["name"], script, "completed", int(time.time())))
        conn.commit()
        
        # 4. Verify Entry
        c.execute("SELECT status, script FROM video_jobs WHERE lead_name = 'Test Lead'")
        row = c.fetchone()
        conn.close()
        
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "completed")
        self.assertEqual(row[1], script)

    def test_video_logic(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._async_test_flow())
        loop.close()

if __name__ == "__main__":
    unittest.main()
