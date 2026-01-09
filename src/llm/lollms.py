from .base import LLMProvider
import json
import os
try:
    from lollms_client import LollmsClient
except ImportError:
    LollmsClient = None

class LollmsProvider(LLMProvider):
    def __init__(self, host=None, port=None, model=None):
        self.host = host or os.getenv("LOLLMS_HOST", "http://localhost")
        self.port = port or os.getenv("LOLLMS_PORT", "9642")
        if LollmsClient:
            self.client = LollmsClient(f"{self.host}:{self.port}")
        else:
            self.client = None
            print("[LollmsProvider] Warning: lollms_client not installed. Provider disabled.")
        self.model = model

    def generate_text(self, prompt, **kwargs):
        """Generates text using lollms-client."""
        try:
            # lollms-client's generate_text might take different args, 
            # but usually it's prompt and then optional params.
            return self.client.generate_text(prompt, **kwargs)
        except Exception as e:
            print(f"[LollmsProvider] Error generating text: {e}")
            return f"Error: {e}"

    def generate_json(self, prompt, **kwargs):
        """Generates JSON using lollms-client."""
        try:
            # LOLLMS often supports structured output via generate_structured_content
            # or we can just parse the text.
            result = self.client.generate_text(prompt, **kwargs)
            # Try to find JSON in the result
            import re
            json_match = re.search(r'(\{.*\}|\[.*\])', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            return {"error": "No JSON found in response", "raw": result}
        except Exception as e:
            print(f"[LollmsProvider] Error generating JSON: {e}")
            return {"error": str(e)}

    async def generate_text_async(self, prompt, **kwargs):
        """Async version of generate_text."""
        # lollms-client might not be natively async, so we use the base implementation's thread wrapper
        return await super().generate_text_async(prompt, **kwargs)

    async def generate_json_async(self, prompt, **kwargs):
        """Async version of generate_json."""
        return await super().generate_json_async(prompt, **kwargs)
