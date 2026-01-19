from src.engine.strategies import (
    WhiteHatOutreachStrategy, 
    GrayHatOutreachStrategy, 
    BlackHatOutreachStrategy
)

class StrategyFactory:
    """
    Factory for instantiating polymorphic strategies based on risk profiles.
    """
    @staticmethod
    def get_outreach_strategy(policy):
        risk = getattr(policy, 'risk_level', 'WHITE_HAT')
        
        if risk == "WHITE_HAT":
            return WhiteHatOutreachStrategy()
        elif risk == "GRAY_HAT":
            return GrayHatOutreachStrategy()
        elif risk == "BLACK_HAT":
            return BlackHatOutreachStrategy()
            
        return WhiteHatOutreachStrategy()
