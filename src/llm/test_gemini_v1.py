import os
import requests
import json
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import config # This triggers load_env()

def test_gemini_v1():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found.")
        return

    # Try v1beta endpoint with exact model name from logs
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": "Hi"}]}]}
    
    print(f"Testing Gemini v1beta endpoint with gemini-flash-latest (proxies disabled)...")
    try:
        # Explicitly disable proxies for this request
        response = requests.post(url, json=payload, timeout=30, proxies={"http": None, "https": None})
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ SUCCESS with v1beta endpoint!")
            print(f"Response: {response.json()['candidates'][0]['content']['parts'][0]['text']}")
        else:
            print(f"❌ FAILED with v1beta endpoint: {response.text}")
    except Exception as e:
        print(f"❌ ERROR with v1beta endpoint: {e}")

if __name__ == "__main__":
    test_gemini_v1()
