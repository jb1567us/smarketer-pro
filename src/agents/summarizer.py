from .base import BaseAgent
import json

class SummarizerAgent(BaseAgent):
    """
    General purpose Text Summarization and Extraction Agent.
    Harveted from LOLLMS 'DocumentSummarizer' and 'Article_Abstractor'.
    """
    def __init__(self, provider=None):
        super().__init__(
            role="Content Synthesizer",
            goal="Condense large documents, articles, or scrape results into concise, actionable summaries.",
            provider=provider
        )

    def summarize_text(self, text, max_words=200, focus_points=None):
        """
        Summarizes text with optional focus points.
        """
        focus_instruction = ""
        if focus_points:
            focus_instruction = f"Focus specifically on these aspects: {', '.join(focus_points)}."
            
        prompt = (
            f"Summarize the following text into approximately {max_words} words.\n"
            f"{focus_instruction}\n\n"
            "TEXT TO SUMMARIZE:\n"
            f"'''{text}'''\n\n"
            "Return JSON with keys: 'summary', 'key_takeaways' (list), 'sentiment'."
        )
        return self.provider.generate_json(prompt)

    def extract_key_points(self, text):
        """
        Extracts bullet points of value from the text.
        """
        prompt = (
            "Extract the main value propositions, facts, or data points from the text below.\n"
            "Ignore fluff and introductory text.\n\n"
            "TEXT:\n"
            f"'''{text}'''\n\n"
            "Return JSON with keys: 'key_points' (list)."
        )
        return self.provider.generate_json(prompt)
