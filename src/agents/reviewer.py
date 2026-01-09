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

    def enhance_email_conversion(self, draft_email):
        """
        Rewrites an email draft to maximize conversion rates, inspired by 'Email Enhancer'.
        Focuses on: Brevity, Clear CTA, "What's in it for them", and removing fluff.
        """
        prompt = (
            "You are a Conversion Rate Optimization (CRO) Expert specialized in Cold Email.\n"
            "Rewrite the following email draft to triple its reply rate.\n\n"
            "RULES:\n"
            "1. Cut the fluff. Be ruthless. Keep it under 150 words if possible.\n"
            "2. Focus entirely on the BENEFIT to the recipient (WIIFM).\n"
            "3. Ensure the Call to Action (CTA) is low friction (e.g., 'Worth a chat?' instead of 'Can we book 30 mins?').\n"
            "4. Remove any 'I hope this finds you well' or generic openers.\n\n"
            "Original Draft:\n"
            f"'''{draft_email}'''\n\n"
            "Return JSON with keys: 'enhanced_subject', 'enhanced_body', 'explanation_of_changes'."
        )
        return self.provider.generate_json(prompt)

    def audit_tone(self, text, target_persona="professional_friend"):
        """
        Deep tone analysis to ensure specific psychological impact.
        """
        prompt = (
            f"Analyze the tone of the following text against the target persona '{target_persona}'.\n"
            "Identify words that sound weak, passive, or overly aggressive.\n\n"
            "Text:\n"
            f"'''{text}'''\n\n"
            "Return JSON with keys: 'current_tone_description', 'tone_score_1_10', 'flagged_phrases' (list), 'suggestions'."
        )
        return self.provider.generate_json(prompt)
