from .base import BaseAgent
from prompt_engine import PromptEngine, PromptContext
import os

class ArtifactDesignerAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Interactive Product Designer",
            goal="Create high-fidelity interactive web artifacts (dashboards, prototypes, reports) using React and Tailwind CSS.",
            provider=provider
        )
        self.prompt_engine = PromptEngine()

    def think(self, concept, instructions=None):
        """
        Generates a web artifact based on a concept.
        """
        # 1. Fetch Context from Hub (if available) or use defaults
        if self.context:
            ctx = self.context
            self.report_to_hub("FETCH_CONTEXT", "Using Hub Brand Kernel for artifact design.")
        else:
            ctx = PromptContext(
                niche="B2B Outreach",
                icp_role="Enterprise Decision Maker",
                brand_voice="Professional, Tech-forward, Reliable",
                product_name="Smarketer-Pro"
            )
            self.report_to_hub("DEFAULT_CONTEXT", "No Hub context found, using defaults.")

        # 2. Render Design Prompt
        design_prompt = self.prompt_engine.get_prompt(
            "designer/web_artifact.j2",
            ctx,
            concept=concept,
            instructions=instructions
        )

        self.report_to_hub("GENERATING_CODE", f"Architecting interactive artifact: {concept[:30]}...")
        
        # 3. Generate React Code
        artifact_code = self.provider.generate_text(design_prompt)
        
        # 4. Wrap in a self-contained previewer HTML (Phase 2 enhancement)
        # For now, we return the raw code and the path where it's saved.
        
        save_path = self._save_artifact(artifact_code, concept)
        
        self.report_to_hub("COMPLETED", f"Artifact saved to {os.path.basename(save_path)}")

        return {
            "type": "web_artifact",
            "concept": concept,
            "code": artifact_code,
            "path": save_path
        }

    def _save_artifact(self, code, concept):
        """Saves the artifact to the data/artifacts directory."""
        import hashlib
        data_dir = os.path.join(os.getcwd(), 'data', 'artifacts')
        os.makedirs(data_dir, exist_ok=True)
        
        clean_concept = "".join([c if c.isalnum() else "_" for c in concept[:20]]).lower()
        file_hash = hashlib.md5(code.encode()).hexdigest()[:8]
        filename = f"artifact_{clean_concept}_{file_hash}.tsx"
        
        path = os.path.join(data_dir, filename)
        with open(path, "w", encoding='utf-8') as f:
            f.write(code)
        return path
