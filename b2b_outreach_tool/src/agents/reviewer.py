from .base import BaseAgent
import json

class ReviewerAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Content Quality & Safety Reviewer",
            goal="Critique email drafts for tone, safety, relevance, and persuasive logic. Identify risks and weak points.",
            provider=provider
        )

    def think(self, context, instructions=None):
        """
        Context should be the email draft or content to review.
        Returns a JSON object with critique.
        """
        base_instructions = (
            "Review the provided email draft. Analyze it for:\n"
            "1. Tone: Is it professional yet engaging?\n"
            "2. Safety: Are there any hallucinations or risky claims?\n"
            "3. Relevance: Does it actually address the recipient's likely needs?\n\n"
            "Return a JSON object with keys: 'approved' (boolean), 'critique' (string, bullet points), 'score' (1-10)."
        )
        
        full_instructions = base_instructions
        if instructions:
            full_instructions += f"\n\nADDITIONAL INSTRUCTIONS:\n{instructions}"

        return self.provider.generate_json(f"Content to Review:\n{context}\n\n{full_instructions}")
