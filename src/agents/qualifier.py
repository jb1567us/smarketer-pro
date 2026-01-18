from .base import BaseAgent
import json
from prompt_engine.interaction import PromptEngine
from prompt_engine.models import PromptContext

class QualifierAgent(BaseAgent):
    def __init__(self, provider=None, prompt_engine=None):
        super().__init__(
            role="Lead Qualification Gatekeeper",
            goal="Strictly evaluate leads against the Ideal Customer Profile (ICP). Reject unqualified leads.",
            provider=provider
        )
        self.prompt_engine = prompt_engine if prompt_engine else PromptEngine()
        # Default empty kernel
        self.kernel = PromptContext(niche="General", icp_role="Evaluator")

    def set_kernel(self, kernel: PromptContext):
        self.kernel = kernel

    def critique_copy(self, content, criteria):
        """
        Evaluates copy using Prompt Engine.
        """
        prompt = self.prompt_engine.get_prompt(
            "qualifier/critique_copy.j2", 
            self.kernel, 
            content=content[:5000], 
            criteria=criteria
        )
        if prompt.startswith("ERROR"):
            self.logger.error(f"Render Error: {prompt}")
            return {"approved": False, "feedback": prompt}
        return self.generate_json(prompt)

    def critique_visuals(self, image_description, criteria):
        """
        Evaluates visuals using Prompt Engine.
        """
        prompt = self.prompt_engine.get_prompt(
            "qualifier/critique_visuals.j2", 
            self.kernel, 
            image_description=image_description, 
            criteria=criteria
        )
        if prompt.startswith("ERROR"):
            self.logger.error(f"Render Error: {prompt}")
            return {"approved": False, "feedback": prompt}
        return self.generate_json(prompt)

    async def think_async(self, context, instructions=None):
        """
        Async evaluation.
        """
        base_instructions = (
            "Evaluate the provided Lead Data against the ICP Criteria.\n"
            "1. Check for all 'Must Haves'.\n"
            "2. Ensure no 'Deal Breakers' are present.\n"
            "3. If strictly matched, approve. If ambiguous, ask for specific clarifications.\n\n"
            "Return JSON: {'qualified': bool, 'score': 0-100, 'reason': str, 'missing_info': str or None}"
        )
        
        full_instructions = base_instructions
        if instructions:
            full_instructions += f"\n\nADDITIONAL INSTRUCTIONS:\n{instructions}"

        return await self.provider.generate_json_async(f"Lead Evaluation Context:\n{context}\n\n{full_instructions}")

    def think(self, context, instructions=None):
        """
        Context should include:
        - Lead Data (HTML content, industry, etc.)
        - ICP Criteria (Must Haves, Deal Breakers)
        """
        base_instructions = (
            "Evaluate the provided Lead Data against the ICP Criteria.\n"
            "1. Check for all 'Must Haves'.\n"
            "2. Ensure no 'Deal Breakers' are present.\n"
            "3. If strictly matched, approve. If ambiguous, ask for specific clarifications.\n\n"
            "Return JSON: {'qualified': bool, 'score': 0-100, 'reason': str, 'missing_info': str or None}"
        )
        
        full_instructions = base_instructions
        if instructions:
            full_instructions += f"\n\nADDITIONAL INSTRUCTIONS:\n{instructions}"

        # Assuming context is a string or dict we can stringify
        return self.provider.generate_json(f"Lead Evaluation Context:\n{context}\n\n{full_instructions}")


    def decide_qualification(self, icp, extracted_signals):
        """
        Hyper-specific qualification decision based on extracted signals and evidence.
        """
        prompt = self.prompt_engine.get_prompt(
            "qualifier/icp_qualification_decider.j2",
            self.kernel,
            icp=icp,
            extracted=extracted_signals
        )
        if prompt.startswith("ERROR"):
            self.logger.error(f"Render Error: {prompt}")
            return {"qualified": False, "error": prompt}
        return self.generate_json(prompt)

    async def decide_qualification_async(self, icp, extracted_signals):
        """
        Async version of decide_qualification.
        """
        prompt = self.prompt_engine.get_prompt(
            "qualifier/icp_qualification_decider.j2",
            self.kernel,
            icp=icp,
            extracted=extracted_signals
        )
        if prompt.startswith("ERROR"):
            self.logger.error(f"Render Error: {prompt}")
            return {"qualified": False, "error": prompt}
        return await self.generate_json_async(prompt)

    def ask_researcher(self, missing_info):
        """
        Helper to formulate a query for the Researcher.
        """
        return f"I cannot verify this lead because I am missing: {missing_info}. Please find evidence of this."
