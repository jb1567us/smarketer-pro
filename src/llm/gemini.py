import os
import requests
import json
import time
from .base import LLMProvider

class GeminiProvider(LLMProvider):
    def __init__(self, api_key, model="gemini-flash-latest"):
        self.api_key = api_key
        self.model = model
        # Strip 'models/' prefix if present to avoid duplication
        clean_model = model.replace("models/", "")
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:generateContent"

    def _call_api(self, payload, **kwargs):
        timeout = kwargs.get('timeout', 30)
        for attempt in range(3):
            try:
                response = requests.post(
                    f"{self.api_url}?key={self.api_key}",
                    headers={'Content-Type': 'application/json'},
                    json=payload,
                    timeout=timeout
                )
                
                if response.status_code == 429:
                    # Fail fast so SmartRouter can switch provider
                    print(f"  [Gemini] Rate limit (429). Triggering failover...")
                    raise Exception("Rate limit exceeded")
                    
                response.raise_for_status()
                return response.json()
                
            except Exception as e:
                # Re-raise if it's our calculated 429 error
                if "Rate limit exceeded" in str(e):
                    raise e
                print(f"  [Gemini] Attempt {attempt+1} failed: {e}")
                time.sleep(2)
        return None

    def generate_text(self, prompt, **kwargs):
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        result = self._call_api(payload, **kwargs)
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
