from .base import BaseAgent

class PromptExpertAgent(BaseAgent):
    """
    Harvested from LOLLMS 'prompting/prompt_expert'.
    Meta-tool for refining and optimizing prompts for other agents.
    """

    def __init__(self, provider=None):
        super().__init__(
            role="PromptExpert",
            goal="Optimize and refine system prompts for maximum LLM performance.",
            backstory=(
                "I am Prompt Expert, an AI assistant specialized in prompt engineering and optimization. "
                "I help users create effective prompts by understanding their goals, applying best practices, "
                "and teaching principles. I maintain a professional yet approachable tone, focusing on "
                "practical solutions."
            ),
            provider=provider
        )

    def analyze_niche(self, niche: str) -> dict:
        """
        Deeply analyzes a niche to extract psychological drivers.
        Returns a dict suitable for populating partial PromptContext.
        """
        self.logger.info(f"🧠 PROMPT EXPERT: Analyzing niche '{niche}' for behavioral drivers...")
        
        prompt = (
            f"You are a World-Class Market Researcher. Analyze the target audience for the '{niche}' industry.\n"
            "Identify the deep psychological drivers, not just surface-level features.\n\n"
            "Return JSON ONLY with this structure:\n"
            "{\n"
            "  'icp_role': 'Specific Role Title (e.g. Busy Mom, CTO, procurement officer)',\n"
            "  'icp_pain_points': ['Pain 1', 'Pain 2', 'Pain 3 (Deep emotional)'],\n"
            "  'icp_desires': ['Desire 1', 'Desire 2 (Transformational)'],\n"
            "  'brand_voice': 'Adjectives describing the ideal tone (e.g. Empathetic but Authoritative)'\n"
            "}"
        )
        
        return self.generate_json(prompt)
