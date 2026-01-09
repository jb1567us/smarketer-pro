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
                    # Include body in error message for blacklist filtering
                    error_msg = f"{response.status_code} Client Error: {response.reason} for url: {self.api_url} Body: {response.text}"
                    print(f"  [GenericLLM] {error_msg}")

                    if response.status_code == 429:
                        print(f"  [GenericLLM] Rate limit hit ({self.model}). Failing over immediately...")
                        raise requests.exceptions.HTTPError(error_msg, response=response)
                    
                    if 400 <= response.status_code < 500:
                        raise requests.exceptions.HTTPError(error_msg, response=response)

                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.HTTPError as e:
                # Propagate 4xx and 429 immediately (do not retry internally)
                if e.response is not None and (e.response.status_code == 429 or 400 <= e.response.status_code < 500):
                    raise e
                # Retry on 5xx
                print(f"  [GenericLLM] Server Error ({self.model}): {e}. Retrying...")
                time.sleep(2)
            except Exception as e:
                print(f"  [GenericLLM] Connection/Other Error ({self.model}): {e}")
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
                            try:
                                text = await response.text()
                            except:
                                text = "N/A"
                            
                            error_msg = f"{response.status} Client Error: {response.reason} for url: {self.api_url} Body: {text}"
                            print(f"  [GenericLLM Async] {error_msg}")

                            if response.status == 429:
                                print(f"  [GenericLLM Async] Rate limit hit ({self.model}). Failing over immediately...")
                                raise aiohttp.ClientResponseError(
                                    response.request_info,
                                    response.history,
                                    status=response.status,
                                    message=error_msg,
                                    headers=response.headers
                                )
                            
                            if 400 <= response.status < 500:
                                raise aiohttp.ClientResponseError(
                                    response.request_info,
                                    response.history,
                                    status=response.status,
                                    message=error_msg,
                                    headers=response.headers
                                )
                            
                        response.raise_for_status()
                        return await response.json()
                
            except aiohttp.ClientResponseError as e:
                 if e.status == 429 or (400 <= e.status < 500):
                     raise e
                 print(f"  [GenericLLM Async] Server Error ({self.model}): {e}. Retrying...")
                 await asyncio.sleep(2)
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
        
        # Helper to clean markdown JSON
        def parse_json_text(text):
            text = text.replace('```json', '').replace('```', '').strip()
            return json.loads(text)

        # Attempt 1: Strict JSON Mode
        try:
            result = self._call_api(messages, response_format={"type": "json_object"})
            if result:
                try:
                    content = result['choices'][0]['message']['content']
                    return json.loads(content)
                except (KeyError, IndexError, json.JSONDecodeError):
                    pass
        except requests.exceptions.HTTPError as e:
            # Fallback for models that don't support json_object (400 Bad Request)
            if e.response.status_code == 400:
                print(f"  [GenericLLM] JSON mode not supported by {self.model} (400). Retrying with text mode...")
                try:
                    # Append strict instruction
                    json_prompt = prompt + "\n\nCRITICAL: Return valid JSON only. No markdown formatting."
                    text_result = self.generate_text(json_prompt, **kwargs)
                    return parse_json_text(text_result)
                except Exception as fallback_e:
                     print(f"  [GenericLLM] Fallback failed: {fallback_e}")
            else:
                # Re-raise other errors (401, 403, 500)
                raise e
        except Exception as e:
            print(f"  [GenericLLM] JSON Gen Error: {e}")

        return None

    async def generate_json_async(self, prompt, **kwargs):
        messages = [{"role": "user", "content": prompt}]
        
        def parse_json_text(text):
            text = text.replace('```json', '').replace('```', '').strip()
            return json.loads(text)

        try:
            result = await self._call_api_async(messages, response_format={"type": "json_object"})
            if result:
                try:
                    content = result['choices'][0]['message']['content']
                    return json.loads(content)
                except (KeyError, IndexError, json.JSONDecodeError):
                    pass
        except aiohttp.ClientResponseError as e:
             if e.status == 400:
                print(f"  [GenericLLM Async] JSON mode not supported by {self.model} (400). Retrying with text mode...")
                try:
                    json_prompt = prompt + "\n\nCRITICAL: Return valid JSON only. No markdown formatting."
                    text_result = await self.generate_text_async(json_prompt, **kwargs)
                    return parse_json_text(text_result)
                except Exception as fallback_e:
                     print(f"  [GenericLLM Async] Fallback failed: {fallback_e}")
             else:
                 raise e
        except Exception as e:
            print(f"  [GenericLLM Async] JSON Gen Error: {e}")
            
        return None
