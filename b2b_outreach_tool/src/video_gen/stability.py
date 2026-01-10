import requests
import time
from .base import VideoProvider

class StabilityProvider(VideoProvider):
    """
    Wrapper for Stability AI Video API.
    Ref: https://platform.stability.ai/docs/api-reference#tag/Image-to-Video
    """
    
    BASE_URL = "https://api.stability.ai/v2beta/image-to-video"

    def generate_video(self, prompt, **kwargs):
        if not self.api_key:
             return {"status": "failed", "error": "Missing API Key"}

        # Stability AI's SVD is primarily Image-to-Video. 
        # Text-to-Video might be different endpoint or require generating image first.
        # For this implementation, we will assume we need to handle Text-to-Video via Image Gen first conceptually,
        # OR check if there is a 'search and replace' or direct text-video endpoint.
        # Actually, standard SVD is Image-to-Video. 
        # But commonly users want Text-to-Video.
        # If the user provides a 'prompt' only, we might need to warn them or generate an image first.
        # However, looking at docs, there IS a 'text-to-video' endpoint often exposed or we chain it. 
        # Let's assume for this "Stub Filling" we might need to be clever.
        # But to keep it simple and working: Stability released "Stable Video Diffusion" which is Image-to-Video.
        # IF we want Text-to-Video, we generate an image from text first, then animate it.
        
        # NOTE: For simplicity, I will implement the Image-to-Video flow. 
        # BUT wait, the arguments are 'prompt'. If 'image' is not in kwargs, we should generate one?
        # Let's check kwargs.
        
        input_image = kwargs.get('image_path')
        if not input_image:
             # Fallback: We can't do pure text-to-video with just SVD easily without an intermediate image generator.
             # We will return an error suggesting usage context or mock it if strictly text.
             # OR we call an image generation endpoint first if we had one.
             return {"status": "failed", "error": "Stability SVD requires an input image. Please provide 'image_path' or use another provider for Text-to-Video."}

        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "seed": kwargs.get("seed", 0),
            "cfg_scale": kwargs.get("cfg_scale", 1.8),
            "motion_bucket_id": kwargs.get("motion_bucket_id", 127)
        }
        
        files = {
            "image": open(input_image, "rb")
        }

        try:
             response = requests.post(
                 self.BASE_URL, 
                 headers=headers, 
                 data=data, 
                 files=files
             )
             
             if response.status_code == 200:
                 data = response.json()
                 return {
                     "job_id": data.get("id"),
                     "status": "processing"
                 }
             else:
                 return {
                     "status": "failed", 
                     "error": f"Stability API Error: {response.status_code} - {response.text}"
                }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def get_status(self, job_id):
        if not self.api_key:
            return {"status": "failed", "error": "Missing API Key"}
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "accept": "video/*"  # Expecting video bytes or status
        }
        
        # Stability logic: GET /v2beta/image-to-video/result/{id}
        url = f"{self.BASE_URL}/result/{job_id}"
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 202:
                # Still running
                return {"status": "processing", "progress": 50}
                
            elif response.status_code == 200:
                # Complete - Note: Stability returns the raw video bytes here usually.
                # We need to save it to a file or upload it.
                # For this 'stub fill', we'll simulate saving to a local 'generated' folder.
                
                # Assume a 'static/generated' folder exists or similar
                # We'll return a data URI or save to disk.
                # Saving to disk is safer.
                import os
                output_path = f"generated_video_{job_id}.mp4"
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                return {
                    "status": "completed",
                    "url": output_path, # Local path, might need serving logic in app.py
                    "progress": 100
                }
                
            else:
                 return {"status": "failed", "error": f"HTTP {response.status_code} - {response.text}"}
                 
        except Exception as e:
            return {"status": "unknown", "error": str(e)}
