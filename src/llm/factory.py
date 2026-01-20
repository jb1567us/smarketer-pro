import os
import sys
from config import config
from .gemini import GeminiProvider
from .openai import OpenAIProvider
from .ollama import OllamaProvider
from .openrouter import OpenRouterProvider
from .openai_compatible import OpenAICompatibleProvider
from .cohere import CohereProvider
from .router import SmartRouter

class LLMFactory:
    _instance = None

    @classmethod
    def get_provider(cls):
        if cls._instance:
            return cls._instance

        llm_config = config.get('llm', {})
        mode = llm_config.get('mode', 'single') # single or router

        if mode == 'router':
            router_config = llm_config.get('router', {})
            candidates = router_config.get('candidates', [])
            if not candidates:
                 print("[LLMFactory] Router mode selected but no candidates defined. Falling back to single provider.")
                 # Fallback to single
            else:
                providers = []
                for candidate in candidates:
                    p_name = candidate.get('provider')
                    m_name = candidate.get('model_name')
                    if p_name:
                         try:
                             provider = cls._create_provider(p_name, m_name)
                             providers.append(provider)
                         except Exception as e:
                             print(f"[LLMFactory] Failed to initialize candidate {p_name}: {e}")
                
                if providers:
                    strategy = router_config.get('strategy', 'priority') 
                    cls._instance = SmartRouter(providers, strategy=strategy)
                    return cls._instance
                else:
                    print("[LLMFactory] No valid router candidates initialized. Falling back.")

        # Default / Single Mode
        provider_name = llm_config.get('provider', 'gemini').lower()
        model_name = llm_config.get('model_name')
        
        try:
            cls._instance = cls._create_provider(provider_name, model_name)
        except Exception as e:
             # Fallback to Gemini if requested failed? Or just raise.
             # For now, let's try to be robust and fallback to Gemini only if not already trying Gemini
             if provider_name != 'gemini':
                 print(f"[LLMFactory] Error initializing {provider_name}: {e}. Falling back to Gemini.")
                 cls._instance = cls._create_provider('gemini', None)
             else:
                 raise e

        return cls._instance

    @staticmethod
    def _create_provider(provider_name, model_name=None):
        if provider_name == 'openai':
            api_key = os.getenv("OPENAI_API_KEY")
            model = model_name or 'gpt-4o-mini'
            return OpenAIProvider(api_key, model)
            
        elif provider_name == 'ollama':
            model = model_name or 'llama3'
            base_url = config.get('llm', {}).get('ollama_base_url', 'http://localhost:11434')
            return OllamaProvider(model, base_url)
            
        elif provider_name == 'openrouter':
            api_key = os.getenv("OPENROUTER_API_KEY")
            model = model_name or 'openai/gpt-3.5-turbo'
            return OpenRouterProvider(api_key, model)

        elif provider_name in ['gemini', 'google_ai_studio']:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                print(f"DEBUG: GEMINI_API_KEY is None! Env dump: {list(os.environ.keys())}")
            model = model_name or 'gemini-flash-latest'
            return GeminiProvider(api_key, model)

        # -- New Providers --

        elif provider_name == 'nvidia': # NVIDIA NIM
            api_key = os.getenv("NVIDIA_API_KEY")
            model = model_name or 'meta/llama3-70b-instruct'
            return OpenAICompatibleProvider(
                api_key, "https://integrate.api.nvidia.com/v1/chat/completions", model
            )

        elif provider_name == 'mistral': # Mistral La Plateforme
            api_key = os.getenv("MISTRAL_API_KEY")
            model = model_name or 'mistral-large-latest'
            return OpenAICompatibleProvider(
                api_key, "https://api.mistral.ai/v1/chat/completions", model
            )

        elif provider_name == 'mistral_codestral':
            api_key = os.getenv("MISTRAL_API_KEY") 
            model = model_name or 'codestral-latest'
            return OpenAICompatibleProvider(
                api_key, "https://api.mistral.ai/v1/chat/completions", model
            )

        elif provider_name == 'huggingface':
            api_key = os.getenv("HUGGINGFACE_API_KEY")
            model = model_name or 'meta-llama/Meta-Llama-3-8B-Instruct'
            return OpenAICompatibleProvider(
                api_key, f"https://api-inference.huggingface.co/models/{model}/v1/chat/completions", model
            )

        elif provider_name == 'cerebras':
            api_key = os.getenv("CEREBRAS_API_KEY")
            model = model_name or 'llama3.1-70b'
            return OpenAICompatibleProvider(
                api_key, "https://api.cerebras.ai/v1/chat/completions", model
            )

        elif provider_name == 'groq':
            api_key = os.getenv("GROQ_API_KEY")
            model = model_name or 'llama-3.3-70b-versatile'
            return OpenAICompatibleProvider(
                api_key, "https://api.groq.com/openai/v1/chat/completions", model
            )
            
        elif provider_name == 'cohere':
            api_key = os.getenv("COHERE_API_KEY")
            model = model_name or 'command-r'
            return CohereProvider(api_key, model)

        elif provider_name == 'github_models':
            api_key = os.getenv("GITHUB_TOKEN")
            model = model_name or 'Phi-3-mini-4k-instruct'
            return OpenAICompatibleProvider(
                api_key, "https://models.inference.ai.azure.com/chat/completions", model
            )
        
        elif provider_name == 'cloudflare':
            account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
            api_key = os.getenv("CLOUDFLARE_API_KEY")
            model = model_name or '@cf/meta/llama-3-8b-instruct'
            return OpenAICompatibleProvider(
                api_key, f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1/chat/completions", model
            )
            
        elif provider_name == 'google_cloud_vertex_ai':
             api_key = os.getenv("GEMINI_API_KEY")
             model = model_name or 'gemini-flash-latest'
             return GeminiProvider(api_key, model)

        raise ValueError(f"Unknown LLM provider: {provider_name}")
