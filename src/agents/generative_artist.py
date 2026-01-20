from .base import BaseAgent
from prompt_engine import PromptEngine, PromptContext
import os

class GenerativeArtAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Generative Artist",
            goal="Express complex brand identities through mathematical patterns and algorithmic motifs using p5.js.",
            provider=provider
        )
        self.prompt_env = PromptEngine()

    def think(self, concept, instructions=None):
        """
        Generates a p5.js visual signature.
        """
        if self.context:
            ctx = self.context
        else:
            ctx = PromptContext(
                niche="Premium Tech",
                icp_role="Innovator",
                brand_voice="Sleek, Minimalist, Mathematical",
                product_name="Smarketer-Pro"
            )

        prompt = self.prompt_env.get_prompt(
            "designer/algo_art.j2",
            ctx,
            concept=concept,
            instructions=instructions
        )

        self.report_to_hub("GENERATING_ALGORITHM", f"Calculating visual signature: {concept[:30]}")
        
        algo_code = self.provider.generate_text(prompt)
        save_path = self._save_art(algo_code, concept)
        
        self.report_to_hub("COMPLETED", f"Visual signature saved to {os.path.basename(save_path)}")

        return {
            "type": "algorithmic_art",
            "concept": concept,
            "html": algo_code,
            "path": save_path
        }

    def _save_art(self, html, concept):
        import hashlib
        data_dir = os.path.join(os.getcwd(), 'data', 'art')
        os.makedirs(data_dir, exist_ok=True)
        
        clean_concept = "".join([c if c.isalnum() else "_" for c in concept[:20]]).lower()
        file_hash = hashlib.md5(html.encode()).hexdigest()[:8]
        filename = f"art_{clean_concept}_{file_hash}.html"
        
        path = os.path.join(data_dir, filename)
        with open(path, "w", encoding='utf-8') as f:
            f.write(html)
        return path
