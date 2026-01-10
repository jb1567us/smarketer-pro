import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))

from llm.factory import LLMFactory
from config import config

def test_lollms_provider():
    # Mock config for lollms
    config['llm']['provider'] = 'lollms'
    config['llm']['lollms_host'] = 'http://localhost'
    config['llm']['lollms_port'] = '9642'
    
    try:
        provider = LLMFactory.get_provider()
        print(f"Successfully got provider: {type(provider).__name__}")
        
        # Note: This test will only fully succeed if a LOLLMS server is actually running.
        # But we can at least check if initialization works.
        print("Integration test complete.")
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_lollms_provider()
