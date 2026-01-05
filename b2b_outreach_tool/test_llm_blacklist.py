
import time
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))
from llm.router import SmartRouter
from llm.base import LLMProvider

class FailingProvider(LLMProvider):
    def __init__(self, name, error_msg):
        self.name = name
        self.error_msg = error_msg
        self.model = "fail-model"

    def generate_text(self, prompt, **kwargs):
        raise Exception(self.error_msg)
    
    def generate_json(self, prompt, **kwargs):
        raise Exception(self.error_msg)

class SuccessProvider(LLMProvider):
    def __init__(self, name):
        self.name = name
        self.model = "success-model"

    def generate_text(self, prompt, **kwargs):
        return "Success"
    
    def generate_json(self, prompt, **kwargs):
        return {"result": "success"}

def test_blacklist():
    print("Testing SmartRouter Blacklisting...")
    
    # 1. Setup providers: one that fails with a terminal error, one that succeeds
    fail_p = FailingProvider("Failing", "400 Bad Request: terms_required")
    success_p = SuccessProvider("Success")
    
    router = SmartRouter([fail_p, success_p], strategy='priority')
    
    # First call: should trigger fail_p, blacklist it, then fallback to success_p
    print("First call (should trigger blacklist)...")
    res1 = router.generate_text("test")
    assert res1 == "Success"
    assert ("FailingProvider", "fail-model") in SmartRouter._blacklist
    print("✅ First call successful and blacklisted.")
    
    # Second call: should skip fail_p entirely
    print("Second call (should skip failing provider)...")
    start_time = time.time()
    res2 = router.generate_text("test")
    end_time = time.time()
    
    assert res2 == "Success"
    # It should be much faster because it skips the exception path
    print(f"✅ Second call successful. Time taken: {end_time - start_time:.4f}s")
    
    print("All LLM Blacklist tests passed!")

if __name__ == "__main__":
    test_blacklist()
