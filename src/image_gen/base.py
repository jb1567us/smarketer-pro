from abc import ABC, abstractmethod

class ImageProvider(ABC):
    @abstractmethod
    def generate_image(self, prompt: str, size: str = "1024x1024", **kwargs) -> str:
        """
        Generates an image from a text prompt.
        Returns the URL or local path to the generated image.
        """
        pass
