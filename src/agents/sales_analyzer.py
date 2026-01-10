from .base import BaseAgent

class SalesAnalyzerAgent(BaseAgent):
    """
    Harvested from LOLLMS 'productivity/meeting_minute_writer'.
    specialized in analyzing sales calls and generating actionable minutes.
    """

    def __init__(self, provider=None):
        super().__init__(
            role="SalesAnalyzer",
            goal="Analyze text transcripts to extract action items, decisions, and summaries.",
            backstory=(
                "Act as a meticulous and attentive listener, taking note of every detail. "
                "Be able to synthesize the information and create comprehensive and accurate minutes "
                "of the meeting. Prioritize accuracy and clarity, while maintaining a neutral tone. "
                "Be efficient and timely in delivering the minutes to all participants."
            ),
            provider=provider
        )
