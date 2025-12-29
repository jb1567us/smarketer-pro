from .base import LLMProvider
import json

class SmartRouter(LLMProvider):
    def __init__(self, providers):
        """
        Args:
            providers (list[LLMProvider]): A list of initialized LLMProvider instances
                                           ordered by priority.
        """
        self.providers = providers

    def generate_text(self, prompt, **kwargs):
        errors = []
        for i, provider in enumerate(self.providers):
            provider_name = provider.__class__.__name__
            # Try to get model name if available for better logging
            model_name = getattr(provider, 'model', 'unknown')
            
            # print(f"  [SmartRouter] Attempting Provider {i+1}/{len(self.providers)}: {provider_name} ({model_name})")
            
            try:
                result = provider.generate_text(prompt, **kwargs)
                if result and isinstance(result, str) and result.strip():
                     # print(f"  [SmartRouter] Success with {provider_name}")
                     return result
                else:
                    errors.append(f"{provider_name}: Empty response")
            except Exception as e:
                errors.append(f"{provider_name}: {str(e)}")
                
        print(f"  [SmartRouter] All providers failed. Errors: {'; '.join(errors)}")
        return ""

    def generate_json(self, prompt, **kwargs):
        errors = []
        for i, provider in enumerate(self.providers):
            provider_name = provider.__class__.__name__
            model_name = getattr(provider, 'model', 'unknown')
            
            # print(f"  [SmartRouter] Attempting JSON Provider {i+1}/{len(self.providers)}: {provider_name} ({model_name})")
            
            try:
                result = provider.generate_json(prompt, **kwargs)
                if result:
                     # print(f"  [SmartRouter] Success with {provider_name}")
                     return result
                else:
                    errors.append(f"{provider_name}: Empty/Invalid JSON")
            except Exception as e:
                errors.append(f"{provider_name}: {str(e)}")

        print(f"  [SmartRouter] All providers failed to generate JSON. Errors: {'; '.join(errors)}")
        return None
