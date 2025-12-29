import requests
import os
import json
from config import config

def fetch_openrouter_models(api_key):
    try:
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        # Sort logic: Free (0.0 cost) -> Cheap -> Expensive
        # Pricing is string like "0.000000" or numeric
        
        def get_price(m):
            try:
                p = m.get('pricing', {})
                prompt = float(p.get('prompt', 0))
                completion = float(p.get('completion', 0))
                return prompt + completion
            except (ValueError, TypeError):
                return 999.0 # Treat unknown as expensive

        models_data = data['data']
        # Sort by price ascending, then by ID
        models_data.sort(key=lambda x: (get_price(x), x['id']))
        
        # Extract IDs
        models = [m['id'] for m in models_data]
        return models
    except Exception as e:
        print(f"Error fetching OpenRouter models: {e}")
        return None

def fetch_ollama_models(base_url):
    try:
        # Strip trailing slash if present for cleaner url join
        base_url = base_url.rstrip('/')
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        response.raise_for_status()
        data = response.json()
        if 'models' in data:
           model_list = data['models']
           # Try to sort nicely if we have metadata
           # Standard Ollama returns: {'name', 'size', 'modified_at', ...}
           # If available, put recent/popular models first if we can guess, or just alpha
           # Users wants "free models first", but for Ollama all are free (unless cloud service)
           # If cloud service mimics OpenRouter, it might have pricing.
           # But let's assume standard Ollama format for now.
           
           def sort_key(m):
               # Prioritize models with 'latest' tag or simple names
               name = m.get('name', '')
               is_latest = 0 if 'latest' in name else 1
               return (is_latest, name)

           model_list.sort(key=sort_key)
           models = [m['name'] for m in model_list]
        else:
            models = []
            
        return models
    except Exception as e:
        print(f"Error fetching Ollama models from {base_url}: {e}")
        return None

def fetch_openai_models(api_key):
    try:
        response = requests.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        # Filter for chat models generally
        models = [m['id'] for m in data['data'] if 'gpt' in m['id']]
        models.sort(reverse=True) # Newest first usually
        return models
    except Exception as e:
        print(f"Error fetching OpenAI models: {e}")
        return None

def fetch_groq_models(api_key):
    try:
        response = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        models = [m['id'] for m in data['data']]
        models.sort()
        return models
    except Exception as e:
        print(f"Error fetching Groq models: {e}")
        return None

def fetch_mistral_models(api_key):
    try:
        response = requests.get(
            "https://api.mistral.ai/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        models = [m['id'] for m in data['data']]
        models.sort(reverse=True)
        return models
    except Exception as e:
        print(f"Error fetching Mistral models: {e}")
        return None

def fetch_gemini_models(api_key):
    try:
        # Google uses a different structure, simplified for now
        # Ideally we use google-generativeai lib, but let's stick to REST if possible or hardcoded fallback
        # Validating models via API key is tricky without the SDK installed.
        # Returning None -> UI keeps using hardcoded defaults
        return None 
    except Exception:
        return None

def fetch_models_for_provider(provider_name):
    """
    Orchestrates fetching based on provider name and env keys.
    """
    if provider_name == 'openrouter':
        key = os.getenv("OPENROUTER_API_KEY")
        if key: return fetch_openrouter_models(key)
        
    elif provider_name == 'ollama':
        url = config.get('llm', {}).get('ollama_base_url', 'http://localhost:11434')
        return fetch_ollama_models(url)
        
    elif provider_name == 'openai':
        key = os.getenv("OPENAI_API_KEY")
        if key: return fetch_openai_models(key)
        
    elif provider_name == 'groq':
        key = os.getenv("GROQ_API_KEY")
        if key: return fetch_groq_models(key)
        
    elif provider_name == 'mistral':
        key = os.getenv("MISTRAL_API_KEY")
        if key: return fetch_mistral_models(key)

    return None
