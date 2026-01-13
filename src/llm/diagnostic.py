import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm.factory import LLMFactory
from llm.router import SmartRouter

def test_provider(provider):
    p_name = provider.__class__.__name__
    m_name = getattr(provider, 'model', 'unknown')
    print(f"\nTesting {p_name} ({m_name})...")
    try:
        response = provider.generate_text("Hi, return 'OK' if you see this.")
        if response and "OK" in response.upper():
            print(f"✅ {p_name} is WORKING.")
            return True
        else:
            print(f"⚠️ {p_name} returned unexpected response: {response}")
            return False
    except Exception as e:
        print(f"❌ {p_name} FAILED: {e}")
        return False

def main():
    print("=== LLM Provider Diagnostic ===")
    try:
        provider = LLMFactory.get_provider()
    except Exception as e:
        print(f"❌ CRITICAL: Failed to initialize LLM Factory: {e}")
        return
    
    if isinstance(provider, SmartRouter):
        print(f"Mode: Router (Strategy: {provider.strategy})")
        print(f"Total Candidates: {len(provider.providers)}")
        for p in provider.providers:
            test_provider(p)
    else:
        print("Mode: Single Provider")
        test_provider(provider)

if __name__ == "__main__":
    main()
