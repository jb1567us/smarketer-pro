import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))

from llm import LLMFactory

def verify_llm():
    print("🧪 Verifying LLM Configuration...")
    
    try:
        provider = LLMFactory.get_provider()
        print(f"✅ Provider loaded: {provider.__class__.__name__}")
        
        if hasattr(provider, 'providers'):
             print(f"   Router Candidates: {[p.__class__.__name__ for p in provider.providers]}")
        elif hasattr(provider, 'model'):
             print(f"   Model: {provider.model}")

        print("\nSending test prompt...")
        response = provider.generate_text("Hello, return the word 'SUCCESS' if you can read this.")
        print(f"Response: {response}")
        
        if "SUCCESS" in response:
            print("✅ Test Passed!")
        else:
            print("⚠️ Response received but keyword missing.")

    except Exception as e:
        print(f"❌ Verification Failed: {e}")

if __name__ == "__main__":
    verify_llm()
