import requests
import os
from config import config

class ModelValidator:
    """
    Validates that the configured LLM models actually exist and are not deprecated.
    """
    
    @staticmethod
    def validate_groq(model_name):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return False, "Missing GROQ_API_KEY"
            
        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            resp = requests.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                valid_ids = [m['id'] for m in data.get('data', [])]
                if model_name in valid_ids:
                    return True, "Valid"
                else:
                    return False, f"Model '{model_name}' not found in Groq. Available: {', '.join(valid_ids[:5])}..."
            else:
                return False, f"API Error {resp.status_code}"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def validate_openrouter(model_name):
        try:
            resp = requests.get("https://openrouter.ai/api/v1/models", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                # OpenRouter list is huge, just check existence
                valid_ids = [m['id'] for m in data.get('data', [])]
                if model_name in valid_ids:
                    return True, "Valid"
                else:
                    return False, f"Model '{model_name}' not found in OpenRouter."
            else:
                 return False, f"API Error {resp.status_code}"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def run_checks():
        print("\n🔍 Validating LLM Configuration...")
        candidates = config.get('llm', {}).get('router', {}).get('candidates', [])
        
        all_valid = True
        for cand in candidates:
            provider = cand.get('provider')
            model = cand.get('model_name')
            
            is_valid = True
            msg = "Skipped check"
            
            if provider == 'groq':
                is_valid, msg = ModelValidator.validate_groq(model)
            elif provider == 'openrouter':
                is_valid, msg = ModelValidator.validate_openrouter(model)
                
            if is_valid:
                print(f"  ✅ {provider}: {model}")
            else:
                print(f"  ❌ {provider}: {model} -> {msg}")
                all_valid = False
                
        return all_valid

if __name__ == "__main__":
    ModelValidator.run_checks()
