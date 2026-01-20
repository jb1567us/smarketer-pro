from abc import ABC, abstractmethod
import logging

from src.prompt_engine.models import PromptContext

class OutreachStrategy(ABC):
    """
    Strategy interface for Outreach campaigns.
    """
    @abstractmethod
    def generate_message_body(self, lead_data: dict, context: PromptContext = None) -> dict:
        pass

class WhiteHatOutreachStrategy(OutreachStrategy):
    """
    White Hat: Deep research, personal hooks, agentic refinement.
    """
    def generate_message_body(self, lead_data: dict, context: PromptContext = None) -> dict:
        from agents import CopywriterAgent
        agent = CopywriterAgent()
        # Pass the kernel context to the agent if available
        return agent.think(lead_data, instructions=f"Context: {context.to_dict() if context else 'None'}")

class GrayHatOutreachStrategy(OutreachStrategy):
    """
    Gray Hat: Segmented templates with minor dynamic injection.
    """
    def generate_message_body(self, lead_data: dict, context: PromptContext = None) -> dict:
        niche = context.niche if context else lead_data.get('niche', 'General')
        product = context.product_name if context else lead_data.get('product_name', 'Smarketer')
        
        return {
            "subject_line": f"Boosting {niche} performance",
            "body": f"Hello {product} team, we noticed your focus on {lead_data.get('pain_point')}...",
            "personalization_explanation": "Gray Hat Template injection"
        }

class BlackHatOutreachStrategy(OutreachStrategy):
    """
    Black Hat: High entropy, spintax, multi-variant testing.
    """
    def generate_message_body(self, lead_data: dict, context: PromptContext = None) -> dict:
        product = context.product_name if context else lead_data.get('product_name', 'Smarketer')
        niche = context.niche if context else lead_data.get('niche', 'General')
        
        return {
            "subject_line": f"Quick Question re: {product}",
            "body": f"Hi, seen your post about {niche}. {lead_data.get('pain_point')} is a mess right now. Check this.",
            "personalization_explanation": "Black Hat Spintax mockup"
        }
