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

    async def generate_text_async(self, prompt, **kwargs):
        """
        Async version of generate_text.
        Default implementation wraps the synchronous method in a thread.
        Subclasses should override this for native async support.
        """
        import asyncio
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: self.generate_text(prompt, **kwargs))

    async def generate_json_async(self, prompt, **kwargs):
        """
        Async version of generate_json.
        Default implementation wraps the synchronous method in a thread.
        Subclasses should override this for native async support.
        """
        import asyncio
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: self.generate_json(prompt, **kwargs))
