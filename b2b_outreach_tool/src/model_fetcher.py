import asyncio
import aiohttp
import os
import json
from config import config
from llm.factory import LLMFactory

NON_ENGLISH_KEYWORDS = [
    "arabic", "saudi", "allam", "orpheus",
    "kimi", "moonshot", "qwen", "alibaba", "tongyi",
    "deepseek", "kat-coder", "xiaomi", "mimo", "glm",
    "chimera", "z-ai", "kwaipilot", "nex-agi"
]

def is_english_model(model_id):
    """Simple heuristic to filter out non-English models based on keywords."""
    model_id_lower = model_id.lower()
    for kw in NON_ENGLISH_KEYWORDS:
        if kw in model_id_lower:
            # Special case: allow 'canopylabs/orpheus-v1-english'
            if "orpheus-v1-english" in model_id_lower:
                return True
            return False
    return True

async def fetch_openrouter_models(session, api_key):
    try:
        async with session.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        ) as response:
            if response.status != 200:
                print(f"OpenRouter Error: {response.status}")
                return []
            data = await response.json()
        
        def get_price(m):
            try:
                p = m.get('pricing', {})
                prompt = float(p.get('prompt', 0))
                completion = float(p.get('completion', 0))
                return prompt + completion
            except (ValueError, TypeError):
                return 999.0

        models_data = data['data']
        models_data.sort(key=lambda x: (get_price(x), x['id']))
        return [m['id'] for m in models_data]
    except Exception as e:
        print(f"Error fetching OpenRouter models: {e}")
        return []

async def fetch_openrouter_free_models(session, api_key):
    try:
        async with session.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        ) as response:
            if response.status != 200:
                print(f"OpenRouter Error: {response.status}")
                return []
            data = await response.json()
        
        free_models = []
        for m in data['data']:
            try:
                p = m.get('pricing', {})
                prompt = float(p.get('prompt', 0))
                completion = float(p.get('completion', 0))
                if prompt == 0 and completion == 0:
                    mid = m['id']
                    if "phi-3-mini-128k-instruct" in mid or "llama-3.1-70b-instruct:free" in mid:
                        continue
                        
                    if is_english_model(mid):
                        free_models.append(mid)
            except (ValueError, TypeError):
                continue
                
        free_models.sort()
        return free_models
    except Exception as e:
        print(f"Error fetching OpenRouter free models: {e}")
        return []

async def fetch_ollama_models(session, base_url, api_key=None):
    try:
        base_url = base_url.rstrip('/')
        headers = {}
        if api_key: headers["Authorization"] = f"Bearer {api_key}"
            
        async with session.get(f"{base_url}/api/tags", headers=headers, timeout=5) as response:
            if response.status != 200: return []
            data = await response.json()

        if 'models' in data:
           model_list = data['models']
           def sort_key(m):
               name = m.get('name', '')
               is_latest = 0 if 'latest' in name else 1
               return (is_latest, name)

           model_list.sort(key=sort_key)
           return [m['name'] for m in model_list]
        return []
    except Exception as e:
        print(f"Error fetching Ollama models from {base_url}: {e}")
        return []

async def fetch_openai_models(session, api_key):
    try:
        async with session.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        ) as response:
            if response.status != 200: return []
            data = await response.json()
        models = [m['id'] for m in data['data'] if 'gpt' in m['id']]
        models.sort(reverse=True)
        return models
    except Exception as e:
        print(f"Error fetching OpenAI models: {e}")
        return []

async def fetch_groq_models(session, api_key):
    try:
        async with session.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        ) as response:
            if response.status != 200: return []
            data = await response.json()
        models = [m['id'] for m in data['data'] if m['id'] != 'mixtral-8x7b-32768']
        models.sort()
        return models
    except Exception as e:
        print(f"Error fetching Groq models: {e}")
        return []

async def fetch_mistral_models(session, api_key):
    try:
        async with session.get(
            "https://api.mistral.ai/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        ) as response:
            if response.status != 200: return []
            data = await response.json()
        models = [m['id'] for m in data['data']]
        models.sort(reverse=True)
        return models
    except Exception as e:
        print(f"Error fetching Mistral models: {e}")
        return []

# Helper to fetch models for settings config
async def fetch_models_for_provider(provider_name):
    async with aiohttp.ClientSession() as session:
        if provider_name == 'openrouter':
            key = os.getenv("OPENROUTER_API_KEY")
            if key: return await fetch_openrouter_models(session, key)
            
        elif provider_name == 'ollama':
            url = config.get('llm', {}).get('ollama_base_url', 'http://localhost:11434')
            key = os.getenv("OLLAMA_API_KEY")
            return await fetch_ollama_models(session, url, api_key=key)
            
        elif provider_name == 'openai':
            key = os.getenv("OPENAI_API_KEY")
            if key: return await fetch_openai_models(session, key)
            
        elif provider_name == 'groq':
            key = os.getenv("GROQ_API_KEY")
            if key: return await fetch_groq_models(session, key)
            
        elif provider_name == 'mistral':
            key = os.getenv("MISTRAL_API_KEY")
            if key: return await fetch_mistral_models(session, key)
    return []

async def get_free_models_for_provider(session, provider_name):
    """Async fetching of free models."""
    if provider_name == 'openrouter':
        key = os.getenv("OPENROUTER_API_KEY")
        if key: return await fetch_openrouter_free_models(session, key)
        
    elif provider_name == 'ollama':
        url = config.get('llm', {}).get('ollama_base_url', 'http://localhost:11434')
        key = os.getenv("OLLAMA_API_KEY")
        return await fetch_ollama_models(session, url, api_key=key)
        
    elif provider_name == 'groq':
        key = os.getenv("GROQ_API_KEY")
        if key: return await fetch_groq_models(session, key)
        
    elif provider_name == 'gemini':
        models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-flash-latest"]
        return [m for m in models if is_english_model(m)]
        
    elif provider_name == 'huggingface':
        return ["meta-llama/Meta-Llama-3-8B-Instruct", "mistralai/Mistral-7B-Instruct-v0.2"]
        
    return []

async def verify_model_access(candidate, log_func=None):
    """Async verification using generate_text_async."""
    provider_name = candidate['provider']
    model_name = candidate['model_name']
    
    try:
        # Instantiate (Sync but usually fast)
        provider = LLMFactory._create_provider(provider_name, model_name)
        
        # Async Gen
        res = await provider.generate_text_async("hi", max_tokens=1, timeout=5)
        if res is not None:
            return True
    except Exception as e:
        # if log_func: log_func(f"Failed: {provider_name}/{model_name}: {e}")
        return False
    return False

async def scan_all_free_providers(status_callback=None):
    def log(msg):
        print(msg, flush=True)
        if status_callback: status_callback(msg)

    candidates = []
    providers_to_check = ['groq', 'gemini', 'openrouter', 'huggingface', 'ollama']
    potential_candidates = []

    print("[Scanner] Phase 1: Fetching Model Lists (Async)...", flush=True)
    if status_callback: status_callback("Phase 1: Fetching model lists from all providers...")

    async with aiohttp.ClientSession() as session:
        # Phase 1: Fetch Concurrent
        tasks = []
        for provider in providers_to_check:
             # Check creds
            skip = False
            if provider == 'groq' and not os.getenv('GROQ_API_KEY'): skip = True
            if provider == 'gemini' and not os.getenv('GEMINI_API_KEY'): skip = True
            if provider == 'openrouter' and not os.getenv('OPENROUTER_API_KEY'): skip = True
            if provider == 'huggingface' and not os.getenv('HUGGINGFACE_API_KEY'): skip = True
            
            if not skip:
                tasks.append((provider, get_free_models_for_provider(session, provider)))
        
        # Await all fetches
        results = await asyncio.gather(*[t[1] for t in tasks], return_exceptions=True)
        
        for i, res in enumerate(results):
            provider = tasks[i][0]
            if isinstance(res, list):
                for m in res:
                    potential_candidates.append({'provider': provider, 'model_name': m})
            else:
                print(f"Error fetching {provider}: {res}")

    if not potential_candidates:
        return []

    print(f"[Scanner] Phase 2: Verifying {len(potential_candidates)} models...", flush=True)
    if status_callback: status_callback(f"Phase 2: Verifying {len(potential_candidates)} candidates concurrently...")

    verified_candidates = []
    sem = asyncio.Semaphore(15) # Limit concurrency to avoid file descriptor limits

    async def sem_verify(cand):
        async with sem:
            is_alive = await verify_model_access(cand)
            if is_alive:
                log(f"  ✅ Verified: {cand['provider']}/{cand['model_name']}")
                cand_copy = cand.copy() # Ensure clean dict
                verified_candidates.append(cand_copy)
                return cand_copy
            else:
                log(f"  ❌ Dead/Unreachable: {cand['provider']}/{cand['model_name']}")
                return None

    # Use wait to ensure we capture all updates
    verification_tasks = [sem_verify(c) for c in potential_candidates]
    if verification_tasks:
        await asyncio.gather(*verification_tasks)

    # Note: verified_candidates list is populated by the coroutines.
    # Since list append is atomic in CPython's GIL (mostly) and we are using await which yields, 
    # it's safer to rely on the return values gathered.
    # But for now, verified_candidates append method works in asyncio single-thread loop.
    
    # Restore Sort Order (Priority)
    final_ordered = []
    # Create unique set of verified for strict equality check
    verified_set = ["{}/{}".format(v['provider'], v['model_name']) for v in verified_candidates]
    
    for p in potential_candidates:
        key = "{}/{}".format(p['provider'], p['model_name'])
        if key in verified_set:
             final_ordered.append(p)
            
    return final_ordered
