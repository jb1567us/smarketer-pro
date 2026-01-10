import requests
import time
from .base import VideoProvider

class LumaProvider(VideoProvider):
    """
    Wrapper for Luma Dream Machine API.
    Ref: https://lumalabs.ai/dream-machine
    """
    
    BASE_URL = "https://api.lumalabs.ai/dream-machine/v1"

    def generate_video(self, prompt, **kwargs):
        if not self.api_key:
             return {"status": "failed", "error": "Missing API Key"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "accept": "application/json"
        }
        
        # Mapping common kwargs to Luma specific parameters
        payload = {
            "prompt": prompt,
            "aspect_ratio": kwargs.get("aspect_ratio", "16:9"),
            "loop": kwargs.get("loop", False)
        }
        
        try:
             # Using the generations endpoint
             response = requests.post(
                 f"{self.BASE_URL}/generations", 
                 json=payload, 
                 headers=headers
            )
             
             if response.status_code == 201 or response.status_code == 200:
                 data = response.json()
                 return {
                     "job_id": data.get("id"),
                     "status": "processing",
                     "provider_response": data
                 }
             else:
                 return {
                     "status": "failed", 
                     "error": f"Luma API Error: {response.status_code} - {response.text}"
                }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def get_status(self, job_id):
        if not self.api_key:
            return {"status": "failed", "error": "Missing API Key"}
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "accept": "application/json"
        }
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/generations/{job_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                state = data.get("state", "unknown")
                
                # Map Luma states to our internal states
                status_map = {
                    "queued": "processing",
                    "dreaming": "processing",
                    "completed": "completed",
                    "failed": "failed"
                }
                
                standard_status = status_map.get(state, "processing")
                
                # Extract video URL if completed
                video_url = None
                if standard_status == "completed":
                    assets = data.get("assets", {})
                    video_url = assets.get("video")
                
                return {
                    "status": standard_status,
                    "url": video_url,
                    "progress": 50 if standard_status == "processing" else 100 if standard_status == "completed" else 0
                }
            else:
                 return {"status": "unknown", "error": f"HTTP {response.status_code}"}
                 
        except Exception as e:
            return {"status": "unknown", "error": str(e)}
