import os
import requests
import json
import time
from config import config
from .base import LLMProvider

class OllamaProvider(LLMProvider):
    def __init__(self, model="llama3", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api/chat"
        # Check for optional API Key (for cloud hosted Ollama)
        self.api_key = os.getenv("OLLAMA_API_KEY")

    def _call_api(self, messages, json_mode=False):
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        if json_mode:
            payload["format"] = "json"

        # Shorter retry logic for local services (usually connection refused if down)
        for attempt in range(3):
            try:
                headers = {"Content-Type": "application/json"}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"

                response = requests.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=300 # Local models can be slow
                )
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.ConnectionError:
                print(f"  [Ollama] Connection failed. Is Ollama running on {self.base_url}?")
                time.sleep(2)
            except Exception as e:
                print(f"  [Ollama] Attempt {attempt+1} failed: {e}")
                time.sleep(2)
        return None

    def generate_text(self, prompt, **kwargs):
        messages = [{"role": "user", "content": prompt}]
        result = self._call_api(messages)
        if result:
            try:
                return result['message']['content']
            except (KeyError, IndexError):
                pass
        return ""

    def generate_json(self, prompt, **kwargs):
        messages = [{"role": "user", "content": prompt}]
        # Ollama supports 'format: json' natively now
        result = self._call_api(messages, json_mode=True)
        if result:
            try:
                content = result['message']['content']
                return json.loads(content)
            except (KeyError, IndexError, json.JSONDecodeError) as e:
                print(f"  [Ollama] JSON Parse Error: {e}")
                pass
        return None
