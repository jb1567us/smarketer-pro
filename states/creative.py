from .base import BaseState
from typing import List, Dict, Any
import reflex as rx
import asyncio
import json

# Check for backend availability
try:
    from backend.database import DB_AVAILABLE, save_creative_content, get_creative_library, save_video_job, get_video_history
except ImportError:
    DB_AVAILABLE = False

class CreativeState(BaseState):
    """State for managing creative assets and generation jobs."""
    
    # Image Designer State
    concept: str = ""
    style: str = "Modern Corporate Memphis"
    aspect_ratio: str = "16:9 (Blog Header)"
    last_design: Dict[str, Any] = {}
    image_library: List[Dict[str, Any]] = []
    
    # Video Studio State
    video_prompt: str = ""
    video_style: str = "Cinematic"
    last_video_job: Dict[str, Any] = {}
    video_library: List[Dict[str, Any]] = []
    
    is_generating_image: bool = False
    is_generating_video: bool = False

    async def load_creative_data(self):
        """Load library data."""
        if not DB_AVAILABLE: return
        
        try:
            self.image_library = await asyncio.to_thread(get_creative_library, "image")
            self.video_library = await asyncio.to_thread(get_video_history)
        except Exception as e:
            self.handle_error(e, "Loading Creative Library")

    async def generate_image(self):
        """Trigger visual generation."""
        if not self.concept:
            self.show_error("Please describe your concept.")
            return

        self.is_generating_image = True
        yield
        
        try:
            from backend.agents.designer import GraphicsDesignerAgent
            designer = GraphicsDesignerAgent()
            res = await designer.think(self.concept, instructions=f"Style: {self.style}. Aspect: {self.aspect_ratio}")
            
            self.last_design = res
            
            # Save to library
            if DB_AVAILABLE:
                await asyncio.to_thread(
                    save_creative_content,
                    type="image",
                    title=self.concept[:50],
                    content_url=res['image_url'],
                    metadata=json.dumps({"prompt": res.get('revised_prompt'), "style": self.style, "base_concept": self.concept})
                )
                yield CreativeState.load_creative_data
                
            self.show_success("Visual asset generated.")
        except Exception as e:
            self.handle_error(e, "Generating Image")
            
        self.is_generating_image = False

    async def generate_video(self):
        """Trigger video generation."""
        if not self.video_prompt:
            self.show_error("Please describe your video idea.")
            return

        self.is_generating_video = True
        yield
        
        try:
            from backend.agents.video_agent import VideoAgent
            agent = VideoAgent()
            result = await asyncio.to_thread(agent.create_video, self.video_prompt, style=self.video_style)
            
            self.last_video_job = result
            
            # Save to history
            if DB_AVAILABLE:
                job_data = result.get('job', {})
                await asyncio.to_thread(
                    save_video_job,
                    prompt=self.video_prompt,
                    optimized_prompt=result.get('optimized_prompt'),
                    provider=result.get('provider'),
                    status=job_data.get('status', 'pending'),
                    job_id=job_data.get('job_id'),
                    url=job_data.get('url')
                )
                yield CreativeState.load_creative_data
                
            self.show_success("Video render initialized.")
        except Exception as e:
            self.handle_error(e, "Generating Video")
            
        self.is_generating_video = False
