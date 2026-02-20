import reflex as rx
import asyncio
import time
from typing import List, Dict, Any
from .base import BaseState
from backend.database import get_connection
from backend.agents.video_agent import VideoAgent

class VideoState(BaseState):
    """Reflex state for Phase 6: AI Video Personalization (Video Lab)."""
    
    video_queue: List[Dict[str, Any]] = []
    is_processing: bool = False
    
    async def poll_video_jobs(self):
        """Update video job statistics from DB."""
        while True:
            try:
                conn = get_connection()
                c = conn.cursor()
                c.execute("SELECT id, lead_name, script, status, video_url, timestamp FROM video_jobs ORDER BY timestamp DESC LIMIT 10")
                self.video_queue = [
                    {
                        "id": r[0],
                        "lead_name": r[1],
                        "script": r[2],
                        "status": r[3],
                        "url": r[4],
                        "ts": r[5]
                    } for r in c.fetchall()
                ]
                conn.close()
            except Exception as e:
                print(f"Video polling error: {e}")
            
            await asyncio.sleep(5)

    async def create_video_job(self, lead_data: Dict[str, Any]):
        """Trigger personalization and job creation for a lead."""
        self.is_processing = True
        self.add_log(f"🎬 Initializing Video Lab for {lead_data.get('name')}...")
        yield
        
        try:
            # 1. Generate Personalized Script
            agent = VideoAgent()
            script = await agent.generate_script(lead_data)
            self.add_log(f"📝 Script Generated for {lead_data.get('name')}.")
            yield
            
            # 2. Insert Job into DB (Pending)
            conn = get_connection()
            c = conn.cursor()
            c.execute('''
                INSERT INTO video_jobs (lead_id, lead_name, script, status, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (lead_data.get("id", 0), lead_data.get("name"), script, "generating", int(time.time())))
            job_id = c.lastrowid
            conn.commit()
            conn.close()
            
            # 3. Simulate Generation Progress
            await asyncio.sleep(2)
            self.add_log(f"📽️ Rendering frames for {lead_data.get('name')}...")
            yield
            await asyncio.sleep(3)
            
            # 4. Finalize Job
            conn = get_connection()
            c = conn.cursor()
            mock_url = "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4"
            c.execute("UPDATE video_jobs SET status = 'completed', video_url = ? WHERE id = ?", (mock_url, job_id))
            conn.commit()
            conn.close()
            
            self.add_log(f"✅ Video Lab: Personalized content ready for {lead_data.get('name')}.")
        except Exception as e:
            self.add_log(f"❌ Video Lab Error: {e}")
            
        self.is_processing = False
        yield
