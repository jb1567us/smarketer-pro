from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class PromptContext:
    """
    The Kernel: Deep Context for the Prompt Engine.
    This object holds the immutable truths about the target audience and niche 
    that should influence every single generated prompt.
    """
    niche: str
    icp_role: str  # e.g. "Homeowner", "CTO", "Procurement Manager"
    icp_pain_points: List[str] = field(default_factory=list)
    icp_desires: List[str] = field(default_factory=list)
    brand_voice: str = "Professional, Authoritative, yet Empathetic"
    product_name: Optional[str] = None
    product_benefits: List[str] = field(default_factory=list)
    
    # Additional raw context if needed
    extra_context: Dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict):
        """Creates a PromptContext from a dictionary (e.g. from the Hub)."""
        return cls(
            niche=data.get('niche', 'General'),
            icp_role=data.get('icp_role', 'Decision Maker'),
            icp_pain_points=data.get('icp_pain_points', []),
            icp_desires=data.get('icp_desires', []),
            brand_voice=data.get('brand_voice', "Professional, Authoritative, yet Empathetic"),
            product_name=data.get('product_name'),
            product_benefits=data.get('product_benefits', []),
            extra_context=data.get('extra_context', {})
        )

    def to_dict(self):
        return {
            "niche": self.niche,
            "icp_role": self.icp_role,
            "icp_pain_points": self.icp_pain_points,
            "icp_desires": self.icp_desires,
            "brand_voice": self.brand_voice,
            "product_name": self.product_name,
            "product_benefits": self.product_benefits,
            "extra_context": self.extra_context
        }
