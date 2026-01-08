from datetime import datetime
from .base import BaseAgent
from video_gen.manager import VideoGenManager

class VideoAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role="Video Director",
            goal="Generate high-quality video content prompts and orchestate video creation."
        )
        self.manager = VideoGenManager()
        
    def generate_video_prompt(self, context, style="cinematic", instructions=None):
        """
        Generates a detailed prompt for the video model based on a rough idea.
        """
        base_instructions = f"""
        You are an expert AIPrompt Engineer for video generation models (like Sora, Gen-3, Kling).
        
        The user wants a video about: {context}
        Style: {style}
        
        Create a detailed, effective prompt that describes the camera movement, lighting, subject action, and atmosphere.
        Return ONLY the prompt text, no pleasantries.
        """
        
        full_instructions = base_instructions
        if instructions:
            full_instructions += f"\n\nADDITIONAL USER INSTRUCTIONS:\n{instructions}"

        res = self.prompt(context, full_instructions).strip()
        self.save_work(res, artifact_type="video_prompt", metadata={"style": style})
        return res
    
    def create_video(self, context, provider_name=None, style="cinematic", instructions=None):
        """
        Orchestrates the full creation flow: prompt generation -> API call.
        """
        # 1. Generate optimized prompt
        optimized_prompt = self.generate_video_prompt(context, style, instructions)
        
        # 2. Select provider
        provider = self.manager.get_provider(provider_name)
        
        # 3. Call execution
        result = provider.generate_video(optimized_prompt)
        

        self.save_work_product(str({
            "optimized_prompt": optimized_prompt,
            "provider": provider_name or self.manager.default_provider,
            "job": result
        }), task_instruction=f"Create video: {context}", tags=["video", "job"])
        
        return {
            "optimized_prompt": optimized_prompt,
            "provider": provider_name or self.manager.default_provider,
            "job": result
        }

    async def think_async(self, context):
        # Implement if needed for async workflows
        pass

    def think(self, context, instructions=None):
        return self.generate_video_prompt(context, instructions=instructions)
