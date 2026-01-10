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
            "Analyze the provided data structure.\n"
            "Suggest the best Streamlit component to display it (e.g., st.dataframe, st.metric, st.bar_chart, st.markdown).\n"
            "Explain why this visualization is best for the user.\n\n"
            "Return a JSON object with keys: 'component_type' (string), 'configuration' (dict), 'reasoning' (string)."
        )
        
        full_instructions = base_instructions
        if instructions:
            full_instructions += f"\n\nADDITIONAL INSTRUCTIONS:\n{instructions}"

        return self.provider.generate_json(f"Data to Visualize:\n{context}\n\n{full_instructions}")
