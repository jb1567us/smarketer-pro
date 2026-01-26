import os
import requests
import json
import time
from .base import LLMProvider

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key, model="gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def _call_api(self, messages, response_format=None):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 1000
        }
        if response_format:
            payload["response_format"] = response_format

        for attempt in range(3):
            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 429:
                    print(f"  [OpenAI] Rate limit hit. FAIL FAST -> Raising to Router.")
                    response.raise_for_status()
                    
                response.raise_for_status()
                return response.json()
                
            except Exception as e:
                print(f"  [OpenAI] Attempt {attempt+1} failed: {e}")
                time.sleep(2)
        return None

    def generate_text(self, prompt, **kwargs):
        messages = [{"role": "user", "content": prompt}]
        result = self._call_api(messages)
        if result:
            try:
                return result['choices'][0]['message']['content']
            except (KeyError, IndexError):
                pass
        return ""

    def generate_json(self, prompt, **kwargs):
        messages = [{"role": "user", "content": prompt}]
        # enforcing json mode
        result = self._call_api(messages, response_format={"type": "json_object"})
        if result:
            try:
                content = result['choices'][0]['message']['content']
                return json.loads(content)
            except (KeyError, IndexError, json.JSONDecodeError):
                pass
        return None
