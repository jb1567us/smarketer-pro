from .base import BaseAgent
import json

class UXAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="User Interface & Experience Designer",
            goal="Decide the best way to visualize data in a Streamlit application.",
            provider=provider
        )

    def think(self, context, instructions=None):
        """
        Context should be the data structure to visualize.
        """
        base_instructions = (
            "Analyze the provided data structure according to UI/UX Pro Max intelligence rules:\n"
            "1. CATEGORY: B2B SaaS Enterprise / Data-Dense Dashboard.\n"
            "2. STYLE: Trust & Authority + Minimalism.\n"
            "3. RECOMMEND: Suggest the best Streamlit component (st.dataframe, st.metric, st.bar_chart, st.markdown).\n"
            "4. REASONING: Explain why this choice builds trust, ROI messaging, or performance efficiency.\n"
            "5. ANTI-PATTERNS: Avoid excessive animation or unreadable color contrasts.\n\n"
            "Return a JSON object with keys: 'component_type' (string), 'configuration' (dict), 'reasoning' (string)."
        )
        
        full_instructions = base_instructions
        if instructions:
            full_instructions += f"\n\nADDITIONAL INSTRUCTIONS:\n{instructions}"

        return self.provider.generate_json(f"Data to Visualize:\n{context}\n\n{full_instructions}")
