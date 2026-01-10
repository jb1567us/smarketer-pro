from .base import BaseAgent
import json

class ProductManagerAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Technical Product Manager / Product Architect",
            goal="Invent and fully specify product functionality, system behavior, and data models.",
            provider=provider
        )

    def think(self, product_idea, instructions=None):
        """
        Analyzes a product idea and generates a build-ready specification.
        """
        base_instructions = (
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
        
        full_instructions = base_instructions
        if instructions:
            full_instructions += f"\n\nADDITIONAL INSTRUCTIONS:\n{instructions}"
            
        prompt = f"Product Idea: {product_idea}\n\n{full_instructions}"
        return self.generate_json(prompt)

    def generate_campaign_strategy(self, product_context, niche="General", instruction_template=None):
        """
        Generates a high-level outreach strategy and campaign concept.
        """
        if instruction_template:
             # Use the custom preset, injecting context variables
            base_instructions = instruction_template.format(niche=niche, product_context=product_context)
            # Ensure JSON format is requested
            instructions = (
                f"{base_instructions}\n\n"
                "Return JSON: {\n"
                "  'strategy_name': str,\n"
                "  'icp_refined': str,\n"
                "  'queries': [str],\n"
                "  'copy_hooks': [str],\n"
                "  'channel_mix': str\n"
                "}"
            )
        else:
            # Default behavior
            instructions = (
                f"Develop a high-level outreach strategy for a campaign in the '{niche}' niche.\n"
                f"Product Context: {product_context}\n"
                "Focus on:\n"
                "1. Ideal Customer Profile (ICP) refinement.\n"
                "2. High-leverage search queries.\n"
                "3. Core emotional hooks for the copywriter.\n"
                "4. Multi-channel touchpoint pattern (Email vs LinkedIn).\n\n"
                "Return JSON: {\n"
                "  'strategy_name': str,\n"
                "  'icp_refined': str,\n"
                "  'queries': [str],\n"
                "  'copy_hooks': [str],\n"
                "  'channel_mix': str\n"
                "}"
            )
        return self.generate_json(instructions)
