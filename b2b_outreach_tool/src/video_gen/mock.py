import time
import uuid
import random
from .base import VideoProvider

class MockProvider(VideoProvider):
    """
    A mock provider that simulates video generation.
    Useful for testing and development without spending credits.
    """
    
    def __init__(self, api_key=None):
        super().__init__(api_key)
        self.jobs = {}

    def generate_video(self, prompt, **kwargs):
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {
            "status": "processing",
            "prompt": prompt,
            "created_at": time.time(),
            "progress": 0
        }
        return {"job_id": job_id, "status": "processing"}

    def get_status(self, job_id):
        job = self.jobs.get(job_id)
        if not job:
            return {"status": "failed", "error": "Job not found"}
        
        # Simulate progress based on time
        elapsed = time.time() - job['created_at']
        if elapsed > 10: # Complete after 10 seconds
            job['status'] = "completed"
            # Random futuristic video placeholder
            job['url'] = "https://media.istockphoto.com/id/1445426963/video/3d-render-abstract-neon-background-with-changing-colors-ultraviolet-light-laser-show-spectrum.mp4?s=mp4-640x640-is&k=20&c=K5g6i-0N3k0h-YwO_z3_8tqC-9tq8_78-83-8q-9-8=" # Placeholder MP4
            job['progress'] = 100
        else:
            job['progress'] = int((elapsed / 10) * 100)
            
        return {
            "status": job['status'],
            "url": job.get('url'),
            "progress": job['progress']
        }
