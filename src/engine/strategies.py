from abc import ABC, abstractmethod
import logging

class OutreachStrategy(ABC):
    """
    Strategy interface for Outreach campaigns.
    """
    @abstractmethod
    def generate_message_body(self, context: dict) -> dict:
        pass

class WhiteHatOutreachStrategy(OutreachStrategy):
    """
    White Hat: Deep research, personal hooks, agentic refinement.
    """
    def generate_message_body(self, context: dict) -> dict:
        from agents import CopywriterAgent
        agent = CopywriterAgent()
        # In a real system, we'd pass 'instructions' if needed.
        return agent.think(context)

class GrayHatOutreachStrategy(OutreachStrategy):
    """
    Gray Hat: Segmented templates with minor dynamic injection.
    """
    def generate_message_body(self, context: dict) -> dict:
        return {
            "subject_line": f"Boosting {context.get('niche')} performance",
            "body": f"Hello {context.get('product_name')} team, we noticed your focus on {context.get('pain_point')}...",
            "personalization_explanation": "Gray Hat Template injection"
        }

class BlackHatOutreachStrategy(OutreachStrategy):
    """
    Black Hat: High entropy, spintax, multi-variant testing.
    """
    def generate_message_body(self, context: dict) -> dict:
        return {
            "subject_line": f"Quick Question re: {context.get('product_name')}",
            "body": f"Hi, seen your post about {context.get('niche')}. {context.get('pain_point')} is a mess right now. Check this.",
            "personalization_explanation": "Black Hat Spintax mockup"
        }
