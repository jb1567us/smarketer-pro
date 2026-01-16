import requests
import json
import time
import aiohttp
import asyncio
from .base import LLMProvider

class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, api_key, api_url, model):
        self.api_key = api_key
        self.api_url = api_url
        self.model = model

    def _call_api(self, messages, response_format=None, **kwargs):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": self.model,
            "messages": messages,
        }
        if response_format:
            payload["response_format"] = response_format

        timeout = kwargs.get('timeout', 60)

        for attempt in range(3):
            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=timeout
                )
                
                if response.status_code != 200:
                    print(f"  [GenericLLM] Status: {response.status_code}, Body: {response.text}")

                if response.status_code == 429:
                    print(f"  [GenericLLM] Rate limit hit ({self.model}). Failing over...")
                    response.raise_for_status()
                    
                response.raise_for_status()
                return response.json()
                
            except Exception as e:
                print(f"  [GenericLLM] Error ({self.model}): {e}")
                time.sleep(2)
        return None

    async def _call_api_async(self, messages, response_format=None):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": self.model,
            "messages": messages,
        }
        if response_format:
            payload["response_format"] = response_format

        for attempt in range(3):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.api_url,
                        headers=headers,
                        json=payload,
                        timeout=60
                    ) as response:
                        
                        if response.status != 200:
                            # Try to wait for text
                            try:
                                text = await response.text()
                            except:
                                text = "N/A"
                            print(f"  [GenericLLM Async] Status: {response.status}, Body: {text}")

                        if response.status == 429:
                            print(f"  [GenericLLM Async] Rate limit hit ({self.model}). Failing over...")
                            response.raise_for_status()
                            
                        response.raise_for_status()
                        return await response.json()
                
            except Exception as e:
                print(f"  [GenericLLM Async] Error ({self.model}): {e}")
                await asyncio.sleep(2)
        return None

    def generate_text(self, prompt, **kwargs):
        messages = [{"role": "user", "content": prompt}]
        result = self._call_api(messages, **kwargs)
        if result:
            try:
                return result['choices'][0]['message']['content']
            except (KeyError, IndexError):
                pass
        return ""

    async def generate_text_async(self, prompt, **kwargs):
        messages = [{"role": "user", "content": prompt}]
        result = await self._call_api_async(messages)
        if result:
            try:
                return result['choices'][0]['message']['content']
            except (KeyError, IndexError):
                pass
        return ""

    def generate_json(self, prompt, **kwargs):
        messages = [{"role": "user", "content": prompt}]
        result = self._call_api(messages, response_format={"type": "json_object"})
        if result:
            try:
                content = result['choices'][0]['message']['content']
                return json.loads(content)
            except (KeyError, IndexError, json.JSONDecodeError):
                pass
        return None

    async def generate_json_async(self, prompt, **kwargs):
        messages = [{"role": "user", "content": prompt}]
        result = await self._call_api_async(messages, response_format={"type": "json_object"})
        if result:
            try:
                content = result['choices'][0]['message']['content']
                return json.loads(content)
            except (KeyError, IndexError, json.JSONDecodeError):
                pass
        return None
