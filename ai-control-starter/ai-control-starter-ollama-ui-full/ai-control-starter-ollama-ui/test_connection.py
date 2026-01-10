import requests
import socket

def check_port():
    """Check if port 11434 is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('localhost', 11434))
        sock.close()
        if result == 0:
            print("✓ Port 11434 is open")
            return True
        else:
            print("✗ Port 11434 is closed")
            return False
    except Exception as e:
        print(f"✗ Port check failed: {e}")
        return False

def test_ollama_simple():
    """Simple test without timeout"""
    try:
        response = requests.get("http://localhost:11434/", timeout=5)
        print(f"✓ Ollama responded with status: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to Ollama - service not running")
        return False
    except Exception as e:
        print(f"✗ Connection test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Ollama connection...")
    
    if not check_port():
        print("\nOllama is not running. Start it with: ollama serve")
        
    if not test_ollama_simple():
        print("\nTroubleshooting:")
        print("1. Open a NEW Command Prompt as Administrator")
        print("2. Run: ollama serve")
        print("3. Keep that window open")
        print("4. Then run this test again")