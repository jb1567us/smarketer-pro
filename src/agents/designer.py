from .base import BaseAgent
import urllib.parse
import random
import requests
import os
import hashlib
import json
from prompt_engine import PromptEngine, PromptContext

class GraphicsDesignerAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Creative Visual Designer",
            goal="Generate high-quality, relevant visual assets for marketing campaigns using generative AI.",
            provider=provider
        )
        self.prompt_engine = PromptEngine()

    def think(self, context, instructions=None):
        """
        Context: The concept or description of the image needed.
        Returns: A URL to the generated image.
        """
        # 1. Build Context (Infer or Default)
        # Often 'context' is "editorial illustration for block post about Roofing"
        # We can try to be smart or just treat it as the 'concept'.
        ctx = PromptContext(
            niche="General", 
            icp_role="General Audience",
            brand_voice="Professional"
        )
        
        # 2. Render Prompt
        refine_prompt = self.prompt_engine.get_prompt(
            "designer/blog_image.j2", 
            ctx, 
            concept=context,
            style=instructions # Pass instructions as style override/addition
        )
        
        image_prompt = self.provider.generate_text(refine_prompt).strip()
        
        # Take only the first line and strip quotes to avoid meta-commentary bloat
        first_line = image_prompt.split('\n')[0].strip()
        clean_prompt = first_line.replace('"', '').replace("'", "").strip()
        
        # Ensure it's not empty, fallback to original context if LLM fails
        if not clean_prompt:
            clean_prompt = context
            
        encoded_prompt = urllib.parse.quote(clean_prompt)
        seed = random.randint(0, 10000)
        
        # Use image.pollinations.ai/prompt/ (Stable legacy bridge)
        # Force model=unity for reliability and add nologo=true
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=576&seed={seed}&model=unity&nologo=true"
        
        # --- Local Download Hack to bypass Streamlit/CDN display issues ---
        local_path = None
        try:
            # Create a local data directory if it doesn't exist
            data_dir = os.path.join(os.getcwd(), 'data', 'images')
            os.makedirs(data_dir, exist_ok=True)
            
            # Create a unique filename based on the prompt hash
            prompt_hash = hashlib.md5(clean_prompt.encode()).hexdigest()
            filename = f"gen_{prompt_hash}_{seed}.png"
            local_path = os.path.join(data_dir, filename)
            
            # Download the image
            print(f"Downloading image for local serving: {image_url}")
            img_data = requests.get(image_url, timeout=20).content
            with open(local_path, "wb") as f:
                f.write(img_data)
            print(f"  Saved to: {local_path}")
        except Exception as e:
            print(f"  Warning: Failed to download image locally: {e}")
            local_path = None # Fallback to URL only

        result = {
            "revised_prompt": image_prompt,
            "image_url": image_url,
            "local_path": local_path,
            "description": context
        }
        
        self.save_work(json.dumps(result), artifact_type="image", metadata={"prompt": clean_prompt})
        return result
