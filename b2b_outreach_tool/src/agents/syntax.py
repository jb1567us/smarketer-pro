from .base import BaseAgent
import json

class SyntaxAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Syntax & Structural Integrity Specialist",
            goal="Ensure content is technically correct, free of placeholders, and properly formatted.",
            provider=provider
        )

    def think(self, context, instructions=None):
        """
        Context should be text or code to validate.
        """
        base_instructions = (
            "Inspect the provided text for:\n"
            "1. Unresolved placeholders (e.g., [Name], {{Company}}).\n"
            "2. Grammatical errors or awkward phrasing.\n"
            "3. Formatting issues.\n\n"
            "Return a JSON object with keys: 'has_errors' (boolean), 'corrected_content' (string), 'issues_found' (list of strings)."
        )
        
        full_instructions = base_instructions
        if instructions:
             full_instructions += f"\n\nADDITIONAL INSTRUCTIONS:\n{instructions}"

        return self.provider.generate_json(f"Content to Validate:\n{context}\n\n{full_instructions}")
