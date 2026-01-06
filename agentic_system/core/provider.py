from abc import ABC, abstractmethod
from typing import Any, Optional

class BaseProvider(ABC):
    """
    Abstract base class for LLM providers.
    """
    
    @abstractmethod
    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generates text based on the prompt.
        """
        pass

    @abstractmethod
    def generate_json(self, prompt: str, schema: Optional[dict] = None) -> dict:
        """
        Generates structured JSON output.
        """
        pass
