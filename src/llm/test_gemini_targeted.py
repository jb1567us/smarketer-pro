import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm.gemini import GeminiProvider

def test_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment.")
        return

    print(f"Key Metadata: Length={len(api_key)}, StartsWith={api_key[:4]}..., EndsWith=...{api_key[-4:]}")
    
    # Test with a few common model names to see which works
    models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-flash-latest"]
    
    for model in models:
        print(f"\nTesting Gemini with model: {model}...")
        provider = GeminiProvider(api_key, model)
        # Manually construct URL to show user what is being called
        clean_model = model.replace("models/", "")
        test_url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:generateContent?key=[MASKED]"
        print(f"Calling URL: {test_url}")
        
        try:
            response = provider.generate_text("Hi, return 'OK' if you see this.")
            if response:
                print(f"✅ SUCCESS with {model}! Response: {response}")
                return
            else:
                print(f"⚠️ {model} returned empty response.")
        except Exception as e:
            print(f"❌ {model} FAILED: {e}")

if __name__ == "__main__":
    test_gemini()
