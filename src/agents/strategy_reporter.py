from .base import BaseAgent
from prompt_engine import PromptEngine, PromptContext
import os
import json

class StrategyReporterAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Strategy & Reporting Consultant",
            goal="Synthesize mission data into professional, client-ready strategy decks, reports, and financial models.",
            provider=provider
        )
        self.prompt_engine = PromptEngine()

    async def think_async(self, format_type="pptx", mission_data=None):
        """
        Generates a professional document based on the requested format.
        """
        # 1. Fetch Context from Hub
        if self.context:
            ctx = self.context
        else:
            ctx = PromptContext(
                niche="B2B Growth",
                icp_role="Founder/CEO",
                brand_voice="Professional & Authoritative",
                product_name="Smarketer-Pro"
            )

        self.report_to_hub("GENERATING_REPORT", f"Building {format_type.upper()} Document...")

        # 2. Render Template for the document structure
        if format_type == "pptx":
            template = "reporting/strategy_deck.j2"
        elif format_type == "xlsx":
            template = "reporting/roi_model.j2"
        else:
            template = "reporting/audit_report.j2"

        doc_structure = self.prompt_engine.get_prompt(
            template,
            ctx,
            mission_data=mission_data
        )

        # 3. Execution Logic
        # In a full implementation, this would call specialized automation scripts.
        # For this phase, we'll implement the logic to save a "Structure Artifact".
        
        save_path = self._save_report(doc_structure, format_type)
        
        self.report_to_hub("COMPLETED", f"{format_type.upper()} saved to {os.path.basename(save_path)}")

        return {
            "type": format_type,
            "structure": doc_structure,
            "path": save_path
        }

    def _save_report(self, content, format_type):
        data_dir = os.path.join(os.getcwd(), 'data', 'reports')
        os.makedirs(data_dir, exist_ok=True)
        
        # In a real scenario, we'd use libraries like python-pptx or openpyxl here.
        # For this integration demo, we save the text-based structure which governs the creation.
        filename = f"strategy_report_{format_type}.txt"
        path = os.path.join(data_dir, filename)
        
        with open(path, "w", encoding='utf-8') as f:
            f.write(content)
        return path
