import sys
import os
from dotenv import load_dotenv

# Force reload of .env
load_dotenv()

def check_keys():
    print("🔑 Checking API Keys...")
    
    groq = os.getenv("GROQ_API_KEY")
    router = os.getenv("OPENROUTER_API_KEY")
    mistral = os.getenv("MISTRAL_API_KEY")
    gemini = os.getenv("GEMINI_API_KEY")
    
    print(f"GROQ_API_KEY: {'[SET]' if groq else '[MISSING]'}")
    print(f"OPENROUTER_API_KEY: {'[SET]' if router else '[MISSING]'}")
    print(f"MISTRAL_API_KEY: {'[SET]' if mistral else '[MISSING]'}")
    print(f"GEMINI_API_KEY: {'[SET]' if gemini else '[MISSING]'}")

    if not groq:
        print("\n❌ CRITICAL: GROQ_API_KEY is missing. Please add it to .env")

check_keys()
