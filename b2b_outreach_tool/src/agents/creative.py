from .base import BaseAgent
import json

class CreativeAgent(BaseAgent):
    """Base for new creative-focused agents."""
    def __init__(self, role, goal, provider=None):
        super().__init__(role, goal, provider=provider)

    def think(self, context):
        """Standard JSON response for creative agents."""
        instructions = (
            "Analyze the provided context and generate high-quality creative output.\n"
            "Return the result ONLY as a RAW JSON object with appropriate fields (e.g., 'title', 'body', 'platform').\n"
            "No markdown, no backticks, no explanations."
        )
        response = self.prompt(context, instructions)
        try:
            # Clean possible markdown wrapping
            clean_res = response.strip().replace('```json', '').replace('```', '').strip()
            return json.loads(clean_res)
        except Exception as e:
            return {"error": "Failed to parse JSON", "raw": response}

class SocialMediaAgent(CreativeAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Expert Social Media Strategist",
            goal="Generate high-engagement social media posts for various platforms.",
            provider=provider
        )

class AdCopyAgent(CreativeAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Direct Response Copywriter",
            goal="Write high-converting ad copy for Google, Facebook, and LinkedIn.",
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
