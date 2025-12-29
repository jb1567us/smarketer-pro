import os
import requests
import json
import time
from .base import LLMProvider

class OpenRouterProvider(LLMProvider):
    def __init__(self, api_key, model="openai/gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

    def _call_api(self, messages, response_format=None):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/b2b-outreach-tool", # OpenRouter requires referer
            "X-Title": "B2B Outreach Agent"
        }
        payload = {
            "model": self.model,
            "messages": messages,
        }
        if response_format:
            payload["response_format"] = response_format

        for attempt in range(3):
            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                
                if response.status_code == 429:
                    wait_time = (attempt + 1) * 10
                    print(f"  [OpenRouter] Rate limit hit. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                    
                response.raise_for_status()
                return response.json()
                
            except Exception as e:
                print(f"  [OpenRouter] Attempt {attempt+1} failed: {e}")
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
        # Helper for models that support JSON mode
        # Many OpenRouter models do not support 'response_format' param strictness like OpenAI
        # So we often rely on prompt engineering, but we can pass it if supported.
        result = self._call_api(messages, response_format={"type": "json_object"})
        if result:
            try:
                content = result['choices'][0]['message']['content']
                # Clean potential markdown
                content = content.replace('```json', '').replace('```', '').strip()
                return json.loads(content)
            except (KeyError, IndexError, json.JSONDecodeError):
                pass
        return None
