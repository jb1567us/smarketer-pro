import asyncio
import random
import time
from .base import LLMProvider

class SmartRouter(LLMProvider):
    # Class-level shared blacklist to survive re-initializations if necessary
    # format: {(provider_name, model_name): expiry_timestamp}
    _blacklist = {}
    _BLACKLIST_DURATION = 900 # 15 minutes

    def __init__(self, providers, strategy='priority'):
        """
        Args:
            providers (list[LLMProvider]): A list of initialized LLMProvider instances
                                           ordered by priority.
        """
        self.providers = providers
        self.strategy = strategy

    def _get_providers_for_request(self):
        """Returns ordered providers based on strategy, skipping blacklisted ones."""
        now = time.time()
        
        # Filter out blacklisted providers
        active_providers = []
        for p in self.providers:
            p_name = p.__class__.__name__
            m_name = getattr(p, 'model', 'unknown')
            key = (p_name, m_name)
            
            if key in self._blacklist:
                if now < self._blacklist[key]:
                    # Still blacklisted
                    continue
                else:
                    # Expired
                    del self._blacklist[key]
            
            active_providers.append(p)

        if not active_providers:
            # If all are blacklisted, reset and try all (emergency fallback)
            print("  [SmartRouter] WARNING: All providers are blacklisted. Resetting blacklist for emergency fallback.")
            self._blacklist.clear()
            active_providers = self.providers

        if self.strategy == 'random':
            # Return shuffled copy to diversify load
            p_copy = active_providers.copy()
            random.shuffle(p_copy)
            return p_copy
        else:
            # Default: Priority order (sequential fallback)
            return active_providers

    def _handle_provider_error(self, provider, error):
        """Decides if a provider should be blacklisted based on the error."""
        p_name = provider.__class__.__name__
        m_name = getattr(provider, 'model', 'unknown')
        err_msg = str(error).lower()
        
        # Non-retryable errors
        blacklist_terms = [
            "terms_required", 
            "400 bad request", 
            "401 unauthorized", 
            "403 forbidden",
            "model_not_found",
            "not authorized"
        ]
        
        should_blacklist = any(term in err_msg for term in blacklist_terms)
        
        if should_blacklist:
            print(f"  [SmartRouter] CRITICAL ERROR from {p_name} ({m_name}): {error}. Blacklisting for 15m.")
            self._blacklist[(p_name, m_name)] = time.time() + self._BLACKLIST_DURATION
        elif "rate limit" in err_msg or "429" in err_msg:
            print(f"  [SmartRouter] {p_name} throttled. Cooling down 5s...")
            time.sleep(1) # Short sleep before next fallback

    def generate_text(self, prompt, **kwargs):
        errors = []
        current_providers = self._get_providers_for_request()
        
        for i, provider in enumerate(current_providers):
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
                self._handle_provider_error(provider, e)
                
        print(f"  [SmartRouter] All active providers failed. Errors: {'; '.join(errors)}")
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
                self._handle_provider_error(provider, e)
                
        print(f"  [SmartRouter] All active providers failed (Async). Errors: {'; '.join(errors)}")
        return ""

    def generate_json(self, prompt, **kwargs):
        errors = []
        current_providers = self._get_providers_for_request()
        for i, provider in enumerate(current_providers):
            provider_name = provider.__class__.__name__
            
            try:
                result = provider.generate_json(prompt, **kwargs)
                if result:
                     return result
                else:
                    errors.append(f"{provider_name}: Empty/Invalid JSON")
            except Exception as e:
                err_msg = str(e)
                errors.append(f"{provider_name}: {err_msg}")
                self._handle_provider_error(provider, e)

        print(f"  [SmartRouter] All active providers failed to generate JSON. Errors: {'; '.join(errors)}")
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
                self._handle_provider_error(provider, e)

        print(f"  [SmartRouter] All active providers failed to generate JSON (Async). Errors: {'; '.join(errors)}")
        return None

