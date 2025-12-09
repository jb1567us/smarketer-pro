import requests
import json
import sys
from pathlib import Path

def test_ollama_connection():
    """Test if Ollama is running and accessible"""
    print("Testing Ollama connection...")
    
    # Test 1: Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            print("✓ Ollama is running")
            models = response.json().get('models', [])
            if models:
                print("Installed models:")
                for model in models:
                    print(f"  - {model.get('name', 'Unknown')}")
            else:
                print("  No models installed")
                return False
        else:
            print(f"✗ Ollama responded with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Cannot connect to Ollama: {e}")
        print("  Make sure Ollama is installed and running")
        return False
    
    # Test 2: Test a simple chat
    try:
        payload = {
            "model": "llama3",
            "stream": False,
            "messages": [
                {"role": "user", "content": "Respond with just 'TEST PASSED'"}
            ],
        }
        
        response = requests.post("http://localhost:11434/api/chat", 
                               json=payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            message = result.get('message', {}).get('content', '')
            print(f"✓ Ollama chat test: {message.strip()}")
            return True
        else:
            print(f"✗ Chat test failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Chat test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_ollama_connection()
    if not success:
        print("\nTroubleshooting steps:")
        print("1. Run 'ollama serve' in a separate terminal")
        print("2. Run 'ollama pull llama3' to download a model")
        print("3. Make sure port 11434 is not blocked")
        sys.exit(1)