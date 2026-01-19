from dataclasses import dataclass
from typing import Optional

@dataclass
class PolicyProfile:
    """
    Defines the Family of Algorithms (White/Gray/Black Hat) for a mission.
    """
    risk_level: str  # "WHITE_HAT", "GRAY_HAT", "BLACK_HAT"
    tool_name: str
    
    @staticmethod
    def default_white_hat(tool_name: str):
        return PolicyProfile(risk_level="WHITE_HAT", tool_name=tool_name)

    @staticmethod
    def default_gray_hat(tool_name: str):
        return PolicyProfile(risk_level="GRAY_HAT", tool_name=tool_name)

    @staticmethod
    def default_black_hat(tool_name: str):
        return PolicyProfile(risk_level="BLACK_HAT", tool_name=tool_name)
