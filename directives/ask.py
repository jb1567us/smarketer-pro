import sys
import os

# Add directive to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from smart_router.factory import LLMFactory

def main():
    if len(sys.argv) < 2:
        print("Usage: python directives/ask.py \"Your prompt\" [tier]")
        sys.exit(1)

    prompt = sys.argv[1]
    tier = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"--- Asking Smart Router (Tier: {tier or 'Default'}) ---")
    try:
        router = LLMFactory.get_provider()
        response = router.generate_text(prompt, tier=tier)
        print("\nResponse:")
        print(response)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
