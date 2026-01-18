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
            
        # Route to image review if context implies it
        prompt_lower = (str(context) + str(instructions)).lower()
        if "image" in prompt_lower or "visual" in prompt_lower or "prompt" in prompt_lower:
             return self.review_image_concept(context, instructions)

        return self.provider.generate_json(f"Content to Review:\n{context}\n\n{full_instructions}")
<<<<<<< HEAD

    def review_content(self, content, criteria=None):
        """
        Evaluates copy against a profile/style guide.
        Absorbed from QualifierAgent.critique_copy.
        """
        criteria_text = f"Criteria: {criteria}" if criteria else "Strictly check for: Tone, Structure, SEO best practices, and prohibited terms."
        prompt = (
            f"You are a Senior Editor. Review the following content.\n"
            f"{criteria_text}\n\n"
            f"Content:\n{content[:4000]}...\n\n"
            "Return JSON: {'approved': bool, 'feedback': 'specific actionable changes if rejected, otherwise 'Good'', 'score': 1-10}"
        )
        return self.generate_json(prompt)

    def review_image_concept(self, image_description, criteria=None):
        """
        Evaluates an image description/prompt against a style guide.
        Absorbed from QualifierAgent.critique_visuals.
        """
        criteria_text = criteria if criteria else "Check for brand alignment, visual clarity, and lack of weird AI artifacts in description."
        prompt = (
            f"You are a Creative Director. Review this image concept/prompt against these criteria: {criteria_text}\n"
            f"Image Concept: {image_description}\n\n"
            "Return JSON: {'approved': bool, 'feedback': 'specific changes to the prompt if rejected', 'score': 1-10}"
        )
        return self.generate_json(prompt)

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
=======
>>>>>>> origin/feature/pc-b-work
