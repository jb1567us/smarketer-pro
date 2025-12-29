from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt, **kwargs):
        """Generates text from the LLM."""
        pass

    @abstractmethod
    def generate_json(self, prompt, **kwargs):
        """Generates valid JSON from the LLM."""
        pass
