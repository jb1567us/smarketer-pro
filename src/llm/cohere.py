import requests
import json
import time
from .base import LLMProvider

class CohereProvider(LLMProvider):
    def __init__(self, api_key, model="command-r"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.cohere.ai/v1/chat"

    def generate_text(self, prompt, **kwargs):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "message": prompt
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            return response.json().get('text', '')
        except Exception as e:
            print(f"  [Cohere] Error: {e}")
            return ""

    def generate_json(self, prompt, **kwargs):
        # Cohere 'response_format' is newer, simpler to prompt for JSON
        prompt += "\n\nRespond strictly with valid JSON."
        text = self.generate_text(prompt)
        try:
            # Clean markdown
            text = text.replace('```json', '').replace('```', '').strip()
            return json.loads(text)
        except:
            return None
