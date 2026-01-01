import requests
import os
import json
import concurrent.futures
from config import config
from llm.factory import LLMFactory

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

def fetch_openrouter_free_models(api_key):
    """Fetches text models from OpenRouter that have 0 cost."""
    try:
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        free_models = []
        for m in data['data']:
            try:
                p = m.get('pricing', {})
                prompt = float(p.get('prompt', 0))
                completion = float(p.get('completion', 0))
                if prompt == 0 and completion == 0:
                    # Blacklist check
                    mid = m['id']
                    if "phi-3-mini-128k-instruct" in mid or "llama-3.1-70b-instruct:free" in mid:
                        continue
                        
                    # Also check if it's a text model (usually context_length > 0)
                    free_models.append(mid)
            except (ValueError, TypeError):
                continue
                
        free_models.sort()
        return free_models
    except Exception as e:
        print(f"Error fetching OpenRouter free models: {e}")
        return None

def fetch_ollama_models(base_url, api_key=None):
    try:
        # Strip trailing slash if present for cleaner url join
        base_url = base_url.rstrip('/')
        
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            
        response = requests.get(f"{base_url}/api/tags", headers=headers, timeout=5)
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
        models = [m['id'] for m in data['data'] if m['id'] != 'mixtral-8x7b-32768']
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
        key = os.getenv("OLLAMA_API_KEY")
        return fetch_ollama_models(url, api_key=key)
        
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

def get_free_models_for_provider(provider_name):
    """
    Returns a list of known free models for the provider.
    Dynamically fetches for OpenRouter, returns hardcoded/known for others.
    """
    if provider_name == 'openrouter':
        key = os.getenv("OPENROUTER_API_KEY")
        if key: return fetch_openrouter_free_models(key)
        
    elif provider_name == 'ollama':
        # All local models are "free" usage-wise
        url = config.get('llm', {}).get('ollama_base_url', 'http://localhost:11434')
        key = os.getenv("OLLAMA_API_KEY")
        return fetch_ollama_models(url, api_key=key)
        
    elif provider_name == 'groq':
        # Groq has a free tier for all models currently (beta), but let's just return all
        key = os.getenv("GROQ_API_KEY")
        if key: return fetch_groq_models(key)
        
    elif provider_name == 'gemini':
        # Gemini Free Tier models
        return ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-flash-latest"]
        
    elif provider_name == 'huggingface':
        # Many are free endpoint compatible
        return ["meta-llama/Meta-Llama-3-8B-Instruct", "mistralai/Mistral-7B-Instruct-v0.2"]
        
    return []

def verify_model_access(candidate, log_func=None):
    """
    Tries to instantiate the provider and generate a tiny response.
    Returns True if successful, False otherwise.
    """
    provider_name = candidate['provider']
    model_name = candidate['model_name']
    
    try:
        # 1. Instantiate
        provider = LLMFactory._create_provider(provider_name, model_name)
        
        # 2. Test Generation
        # Use a very short timeout/prompt
        res = provider.generate_text("hi", max_tokens=1, timeout=3)
        if res is not None: 
            return True
    except Exception as e:
        # if log_func: log_func(f"  [Verification Failed] {provider_name}/{model_name}: {e}")
        return False
        
    return False

def scan_all_free_providers(status_callback=None):
    """
    Iterates through all supported providers, checks for API keys/availability,
    fetches lists, AND actively verifies they accept requests.
    Returns a list of candidate dicts: [{'provider': 'groq', 'model_name': '...'}, ...]
    """
    def log(msg):
        print(msg, flush=True)
        if status_callback:
            status_callback(msg)

    candidates = []
    
    # Priority Order for Free Tier Performance/Speed
    # 1. Groq (Fastest)
    # 2. Gemini (High Quality, generous limits)
    # 3. OpenRouter (Aggregation of free models)
    # 4. HuggingFace (Good backups)
    # 5. Ollama (Local)
    
    providers_to_check = ['groq', 'gemini', 'openrouter', 'huggingface', 'ollama']
    
    potential_candidates = []

    print("[Scanner] Phase 1: Fetching Model Lists...")
    for provider in providers_to_check:
        try:
            # Check if we have credentials before trying (optimization)
            skip = False
            if provider == 'groq' and not os.getenv('GROQ_API_KEY'): skip = True
            if provider == 'gemini' and not os.getenv('GEMINI_API_KEY'): skip = True
            if provider == 'openrouter' and not os.getenv('OPENROUTER_API_KEY'): skip = True
            if provider == 'huggingface' and not os.getenv('HUGGINGFACE_API_KEY'): skip = True
            
            if not skip:
                models = get_free_models_for_provider(provider)
                if models:
                    for m in models:
                        potential_candidates.append({
                            'provider': provider,
                            'model_name': m
                        })
        except Exception as e:
            print(f"Error scanning {provider} for free models: {e}")
            continue
            
    # Phase 2: Active Verification
    if not potential_candidates:
        return []
        
    print(f"[Scanner] Phase 2: Verifying {len(potential_candidates)} models (Active Ping)...", flush=True)
    if status_callback: status_callback(f"Phase 2: Verifying {len(potential_candidates)} models...")
    
    verified_candidates = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        # Map future to candidate
        future_to_cand = {executor.submit(verify_model_access, c): c for c in potential_candidates}
        
        for future in concurrent.futures.as_completed(future_to_cand):
            cand = future_to_cand[future]
            try:
                is_alive = future.result()
                if is_alive:
                    verified_candidates.append(cand)
                    log(f"  ✅ Verified: {cand['provider']}/{cand['model_name']}")
                else:
                    log(f"  ❌ Dead/Unreachable: {cand['provider']}/{cand['model_name']}")
            except Exception as e:
                 log(f"  ❌ Error verifying {cand['provider']}/{cand['model_name']}: {e}")

    # Restore Sort Order (Priority) from original list preference
    # Verified candidates might be scrambled due to async completion
    # We want to maintain: Groq -> Gemini -> OpenRouter etc.
    # Simple way: iterate through potential_candidates and pick if in verified
    
    final_ordered = []
    for potentials in potential_candidates:
        if potentials in verified_candidates:
            final_ordered.append(potentials)
            
    return final_ordered
