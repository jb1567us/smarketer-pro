import os
import requests
import json

key = os.environ.get("GEMINI_API_KEY")
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
print(f"Querying: {url.replace(key, 'HIDDEN')}")

try:
    res = requests.get(url)
    res.raise_for_status()
    models = res.json().get('models', [])
    print(f"Found {len(models)} models:")
    for m in models:
        if 'generateContent' in m.get('supportedGenerationMethods', []):
            print(f" - {m['name']}")
except Exception as e:
    print(f"Error: {e}")
    if 'res' in locals():
        print(res.text)
