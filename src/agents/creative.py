from .base import BaseAgent
import json

class CreativeAgent(BaseAgent):
    """Base for new creative-focused agents."""
    def __init__(self, role, goal, provider=None):
        super().__init__(role, goal, provider=provider)

    def think(self, context, instructions=None):
        """Standard JSON response for creative agents."""
        base_instructions = (
            "Analyze the provided context and generate high-quality creative output.\n"
            "Return the result ONLY as a RAW JSON object with appropriate fields (e.g., 'title', 'body', 'platform').\n"
            "No markdown, no backticks, no explanations."
        )
        
        full_instructions = base_instructions
        if instructions:
             full_instructions = f"{instructions}\n\n{base_instructions}" # Prepend or append? Let's prepend user instructions or mix.
             # Actually, user instructions should probably GUIDE the creative output.
             full_instructions = f"{base_instructions}\n\nADDITIONAL GUIDANCE:\n{instructions}"

        response = self.prompt(context, full_instructions)
        try:
            # Clean possible markdown wrapping
            clean_res = response.strip().replace('```json', '').replace('```', '').strip()
            return json.loads(clean_res)
        except Exception as e:
            return {"error": "Failed to parse JSON", "raw": response}

    def tune(self, context, previous_response, instructions, history=None):
        """Standard JSON response for tuning creative agents."""
        tune_instructions = (
            f"REFINE the previous output based on these instructions:\n{instructions}\n\n"
            "Return the result ONLY as a RAW JSON object. No markdown, no backticks, no explanations."
        )
        # We need to construct the prompt manually here to ensure JSON format, 
        # or call base tune and then parse. Let's call base tune and parse.
        response = super().tune(context, previous_response, tune_instructions, history=history)
        try:
            clean_res = response.strip().replace('```json', '').replace('```', '').strip()
            return json.loads(clean_res)
        except Exception as e:
            return {"error": "Failed to parse JSON during tuning", "raw": response}

    def discuss(self, context, previous_response, message, history=None):
        """Standard discussion for creative agents (returns plain text)."""
        return super().discuss(context, previous_response, message, history=history)

class SocialMediaAgent(CreativeAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Expert Social Media Strategist",
            goal="Generate high-engagement social media posts for various platforms.",
            backstory=(
                "You are the Social Media Strategist, harvested from LOLLMS 'internet/social_media_manager'. "
                "You embody the 'Show, Don't Tell' philosophy. Your posts are not just text; they are engagement traps. "
                "You understand hook structures, viral loops, and platform-specific nuances. You write like a human, not an AI."
            ),
            provider=provider
        )

    def generate_tiktok_strategy(self, niche, product_name):
        context = f"Niche: {niche}, Product: {product_name}, Platform: TikTok"
        instructions = "Generate a viral TikTok strategy including video hooks, trending audio types, and hashtag clusters. Return JSON."
        return self.think(f"{context}\n\n{instructions}")

    def generate_instagram_strategy(self, niche, product_name):
        context = f"Niche: {niche}, Product: {product_name}, Platform: Instagram"
        instructions = "Generate an Instagram strategy covering Reels, Stories, and Grid posts. Include aesthetic direction. Return JSON."
        return self.think(f"{context}\n\n{instructions}")

class AdCopyAgent(CreativeAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Direct Response Copywriter",
            goal="Write high-converting ad copy for Google, Facebook, and LinkedIn.",
            backstory=(
                "You are the Direct Response Copywriter, harvested from LOLLMS 'marketing/copywriter'. "
                "You don't write 'ads'; you write money-printing machines. You follow the principles of Ogilvy and Hopkins. "
                "Every word must earn its keep. You focus on: Hook, Story, Offer. You are persuasive, urgent, and benefit-driven."
            ),
            provider=provider
        )

class BrainstormerAgent(CreativeAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Creative Campaign Director",
            goal="Brainstorm innovative campaign angles, hooks, and themes.",
            provider=provider
        )

class PersonaAgent(CreativeAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Market Research Analyst",
            goal="Create detailed Ideal Customer Personas (ICPs) based on market data.",
            provider=provider
        )
