import os
import requests
import json
import time
from .base import LLMProvider

class GeminiProvider(LLMProvider):
    def __init__(self, api_key, model="gemini-flash-latest"):
        self.api_key = api_key
        self.model = model
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def _call_api(self, payload):
        for attempt in range(3):
            try:
                response = requests.post(
                    f"{self.api_url}?key={self.api_key}",
                    headers={'Content-Type': 'application/json'},
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 429:
                    wait_time = (attempt + 1) * 15
                    print(f"  [Gemini] Rate limit hit. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                    
                response.raise_for_status()
                return response.json()
                
            except Exception as e:
                print(f"  [Gemini] Attempt {attempt+1} failed: {e}")
                time.sleep(2)
        return None

    def generate_text(self, prompt, **kwargs):
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        result = self._call_api(payload)
        if result:
            try:
                return result['candidates'][0]['content']['parts'][0]['text']
            except (KeyError, IndexError):
                pass
        return ""

    def generate_json(self, prompt, **kwargs):
        # Gemini often needs explicit JSON instruction reinforcement
        json_prompt = prompt + "\n\nReturn valid JSON only. No markdown formatting."
        text = self.generate_text(json_prompt)
        text = text.replace('```json', '').replace('```', '').strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            print(f"  [Gemini] Failed to parse JSON response: {text[:50]}...")
            return None
