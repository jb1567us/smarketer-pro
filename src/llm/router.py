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
            providers (list[dict]): List of dicts with 'instance' (LLMProvider) and 'tier' ('performance'|'economy')
        """
        self.providers = providers # [{'instance': p, 'tier': 'economy'}]
        self.strategy = strategy

    def _get_providers_for_request(self, target_tier=None):
        """Returns ordered providers based on strategy, skipping blacklisted ones."""
        from config import config
        now = time.time()
        mode = config.get('project', {}).get('performance_mode', 'paid')
        
        # 1. Filter out blacklisted and check mode
        candidates = []
        for p_entry in self.providers:
            p = p_entry['instance']
            tier = p_entry.get('tier', 'economy')
            
            p_name = p.__class__.__name__.lower()
            m_name = getattr(p, 'model', 'unknown').lower()
            key = (p.__class__.__name__, getattr(p, 'model', 'unknown'))
            
            # Check Mode Constraints
            if mode == 'free':
                is_free = 'ollama' in p_name or ':free' in m_name
                if not is_free: continue
            
            if key in self._blacklist:
                if now < self._blacklist[key]:
                    continue
                else:
                    del self._blacklist[key]
            
            candidates.append({'instance': p, 'tier': tier})

        if not candidates:
            # If all are blacklisted, reset and try all (emergency fallback)
            print("  [SmartRouter] WARNING: All providers are blacklisted. Resetting blacklist.")
            self._blacklist.clear()
            candidates = self.providers

        # 2. Tier Selection Logic
        if target_tier:
            primary = [c['instance'] for c in candidates if c['tier'] == target_tier]
            secondary = [c['instance'] for c in candidates if c['tier'] != target_tier]
            ordered_candidates = primary + secondary
        else:
            ordered_candidates = [c['instance'] for c in candidates]

        if self.strategy == 'random':
            random.shuffle(ordered_candidates)
            
        return ordered_candidates

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
             print(f"  [SmartRouter] {p_name} throttled. Blacklisting for 60s to failover...")
             # Blacklist for 1 minute to allow rotation to other keys
             self._blacklist[(p_name, m_name)] = time.time() + 60

    def generate_text(self, prompt, **kwargs):
        tier = kwargs.pop('tier', None)
        errors = []
        current_providers = self._get_providers_for_request(target_tier=tier)
        
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
        tier = kwargs.pop('tier', None)
        errors = []
        current_providers = self._get_providers_for_request(target_tier=tier)
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
        tier = kwargs.pop('tier', None)
        errors = []
        current_providers = self._get_providers_for_request(target_tier=tier)
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
        tier = kwargs.pop('tier', None)
        errors = []
        current_providers = self._get_providers_for_request(target_tier=tier)
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

    def get_status(self):
        """Returns the health status of all providers."""
        now = time.time()
        status_list = []
        for p in self.providers:
            key = (p.__class__.__name__, getattr(p, 'model', 'unknown'))
            is_blacklisted = key in self._blacklist and now < self._blacklist[key]
            status_list.append({
                "provider": key[0],
                "model": key[1],
                "active": not is_blacklisted,
                "until": self._blacklist[key] if is_blacklisted else None
            })
        return status_list

    async def run_health_check(self):
        """Concurrently checks health of candidates."""
        tasks = []
        for provider in self.providers:
             tasks.append(self._check_provider_health(provider))
        return await asyncio.gather(*tasks)

    async def _check_provider_health(self, provider):
        key = (provider.__class__.__name__, getattr(provider, 'model', 'unknown'))
        try:
            # Short timeout, minimal tokens
            res = await provider.generate_text_async("hi", max_tokens=1, timeout=5)
            if res:
                return {"provider": key[0], "model": key[1], "status": "healthy"}
            return {"provider": key[0], "model": key[1], "status": "unhealthy", "error": "Empty response"}
        except Exception as e:
            # This will update the blacklist if error is severe
            self._handle_provider_error(provider, e)
            return {"provider": key[0], "model": key[1], "status": "down", "error": str(e)}

