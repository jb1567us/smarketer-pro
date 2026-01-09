import sys
from pathlib import Path

# Add the parent directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

try:
    import model_client
    from model_client import ModelClientError
    print("✓ Model client imported successfully")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

def test_model_generation():
    """Test the model client with a simple prompt"""
    system_prompt = "You are a helpful assistant. Respond with just 'TEST PASSED'."
    user_prompt = "Please respond with exactly: TEST PASSED"
    
    try:
        print("Testing model generation...")
        response = model_client.generate_text(
            system_prompt, 
            user_prompt, 
            task="planning"
        )
        print(f"✓ Model generation SUCCESS: {response.strip()}")
        return True
    except ModelClientError as e:
        print(f"✗ Model generation FAILED: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_model_generation()
    if not success:
        print("\nTroubleshooting:")
        print("1. Check model_config.json exists")
        print("2. Run: python scripts/auto_configure_models.py")
        print("3. Verify Ollama is running: ollama list")
        sys.exit(1)