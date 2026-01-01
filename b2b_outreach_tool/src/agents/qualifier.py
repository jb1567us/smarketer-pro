from .base import BaseAgent
import json

class QualifierAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Lead Qualification Gatekeeper",
            goal="Strictly evaluate leads against the Ideal Customer Profile (ICP). Reject unqualified leads.",
            provider=provider
        )

    async def think_async(self, context):
        """
        Async evaluation.
        """
        instructions = (
            "Evaluate the provided Lead Data against the ICP Criteria.\n"
            "1. Check for all 'Must Haves'.\n"
            "2. Ensure no 'Deal Breakers' are present.\n"
            "3. If strictly matched, approve. If ambiguous, ask for specific clarifications.\n\n"
            "Return JSON: {'qualified': bool, 'score': 0-100, 'reason': str, 'missing_info': str or None}"
        )
        return await self.provider.generate_json_async(f"Lead Evaluation Context:\n{context}\n\n{instructions}")

    def think(self, context):
        """
        Context should include:
        - Lead Data (HTML content, industry, etc.)
        - ICP Criteria (Must Haves, Deal Breakers)
        """
        instructions = (
            "Evaluate the provided Lead Data against the ICP Criteria.\n"
            "1. Check for all 'Must Haves'.\n"
            "2. Ensure no 'Deal Breakers' are present.\n"
            "3. If strictly matched, approve. If ambiguous, ask for specific clarifications.\n\n"
            "Return JSON: {'qualified': bool, 'score': 0-100, 'reason': str, 'missing_info': str or None}"
        )
        # Assuming context is a string or dict we can stringify
        return self.provider.generate_json(f"Lead Evaluation Context:\n{context}\n\n{instructions}")

    def ask_researcher(self, missing_info):
        """
        Helper to formulate a query for the Researcher.
        """
        return f"I cannot verify this lead because I am missing: {missing_info}. Please find evidence of this."
