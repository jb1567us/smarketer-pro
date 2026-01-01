from .base import BaseAgent
import json

class CopywriterAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="B2B Email Copywriter",
            goal="Draft highly personalized, persuasive, and human-sounding cold emails based on verified lead data.",
            provider=provider
        )

    def think(self, context):
        """
        Context should include:
        - Lead info (Business type, pain points, contact name)
        - Value Proposition (what we are selling)
        """
        instructions = (
            "Draft a cold email for this lead.\n"
            "Rules:\n"
            "1. Use a hook relevant to their specific business (use the provided analysis).\n"
            "2. Keep it under 150 words.\n"
            "3. End with a soft call to action (e.g. 'Worth a chat?').\n"
            "4. Do NOT use generic fluff like 'I hope this finds you well'.\n\n"
            "Return JSON: {'subject_line': str, 'body': str, 'personalization_explanation': str}"
        )
        return self.provider.generate_json(f"Context for Email:\n{context}\n\n{instructions}")
