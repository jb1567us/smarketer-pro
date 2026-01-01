import asyncio
import random
import time
from .base import LLMProvider

class SmartRouter(LLMProvider):
    def __init__(self, providers, strategy='priority'):
        """
        Args:
            providers (list[LLMProvider]): A list of initialized LLMProvider instances
                                           ordered by priority.
        """
        self.providers = providers
        self.strategy = strategy

    def _get_providers_for_request(self):
        """Returns ordered providers based on strategy"""
        if self.strategy == 'random':
            # Return shuffled copy to diversify load
            p_copy = self.providers.copy()
            random.shuffle(p_copy)
            return p_copy
        else:
            # Default: Priority order (sequential fallback)
            return self.providers

    def generate_text(self, prompt, **kwargs):
        errors = []
        for i, provider in enumerate(self.providers):
            provider_name = provider.__class__.__name__
            model_name = getattr(provider, 'model', 'unknown')
            
            try:
                result = provider.generate_text(prompt, **kwargs)
                if result and isinstance(result, str) and result.strip():
                     return result
                else:
                    errors.append(f"{provider_name}: Empty response")
            except Exception as e:
                err_msg = str(e)
                errors.append(f"{provider_name}: {err_msg}")
                # Cool down on rate limit before trying next provider
                if "rate limit" in err_msg.lower() or "429" in err_msg:
                    print(f"  [SmartRouter] {provider_name} throttled. Cooling down 5s...")
                    time.sleep(5)
                
        print(f"  [SmartRouter] All providers failed. Errors: {'; '.join(errors)}")
        return ""

    async def generate_text_async(self, prompt, **kwargs):
        errors = []
        current_providers = self._get_providers_for_request()
        for i, provider in enumerate(current_providers):
            provider_name = provider.__class__.__name__
            
            try:
                result = await provider.generate_text_async(prompt, **kwargs)
                if result and isinstance(result, str) and result.strip():
                     return result
                else:
                    errors.append(f"{provider_name}: Empty response")
            except Exception as e:
                err_msg = str(e)
                errors.append(f"{provider_name}: {err_msg}")
                if "rate limit" in err_msg.lower() or "429" in err_msg:
                     print(f"  [SmartRouter] {provider_name} throttled. Cooling down 5s...")
                     await asyncio.sleep(5)
                
        print(f"  [SmartRouter] All providers failed (Async). Errors: {'; '.join(errors)}")
        return ""

    def generate_json(self, prompt, **kwargs):
        errors = []
        current_providers = self._get_providers_for_request()
        for i, provider in enumerate(current_providers):
            provider_name = provider.__class__.__name__
            model_name = getattr(provider, 'model', 'unknown')
            
            try:
                result = provider.generate_json(prompt, **kwargs)
                if result:
                     return result
                else:
                    errors.append(f"{provider_name}: Empty/Invalid JSON")
            except Exception as e:
                err_msg = str(e)
                errors.append(f"{provider_name}: {err_msg}")
                if "rate limit" in err_msg.lower() or "429" in err_msg:
                     print(f"  [SmartRouter] {provider_name} throttled. Cooling down 5s...")
                     time.sleep(5)

        print(f"  [SmartRouter] All providers failed to generate JSON. Errors: {'; '.join(errors)}")
        return None

    async def generate_json_async(self, prompt, **kwargs):
        errors = []
        current_providers = self._get_providers_for_request()
        for i, provider in enumerate(current_providers):
            provider_name = provider.__class__.__name__
            
            try:
                result = await provider.generate_json_async(prompt, **kwargs)
                if result:
                     return result
                else:
                    errors.append(f"{provider_name}: Empty/Invalid JSON")
            except Exception as e:
                err_msg = str(e)
                errors.append(f"{provider_name}: {err_msg}")
                if "rate limit" in err_msg.lower() or "429" in err_msg:
                     print(f"  [SmartRouter] {provider_name} throttled. Cooling down 5s...")
                     await asyncio.sleep(5)

        print(f"  [SmartRouter] All providers failed to generate JSON (Async). Errors: {'; '.join(errors)}")
        return None
