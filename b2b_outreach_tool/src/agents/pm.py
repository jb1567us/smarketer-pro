from .base import BaseAgent
import json

class ProductManagerAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Technical Product Manager / Product Architect",
            goal="Invent and fully specify product functionality, system behavior, and data models.",
            provider=provider
        )

    def think(self, product_idea):
        """
        Analyzes a product idea and generates a build-ready specification.
        """
        instructions = (
            "Given the following product idea, provide a comprehensive technical specification.\n"
            "Focus on IDEATION, system behavior, contracts, and build-ready specs.\n"
            "Include the following sections in your response:\n"
            "1. Core Functionality & Workflows\n"
            "2. Edge Cases & Constraints\n"
            "3. Functional Requirements\n"
            "4. Acceptance Criteria\n"
            "5. Data Models (if applicable)\n\n"
            "IMPORTANT: Do not design UI/UX. Focus on back-end logic and system behavior.\n"
            "Return the result as a JSON object with keys: 'product_name', 'summary', 'workflows', 'edge_cases', 'requirements', 'acceptance_criteria', 'data_models'."
        )
        
        prompt = f"Product Idea: {product_idea}\n\n{instructions}"
        return self.provider.generate_json(prompt)
