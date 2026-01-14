import sys
import os
import time
import threading

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from automation_engine import AutomationEngine
from agents.researcher import ResearcherAgent

def test_async_execution():
    print("🚀 Initializing Automation Engine...")
    engine = AutomationEngine()
    
    print("🤖 Initializing Researcher Agent...")
    try:
        agent = ResearcherAgent()
        
        # Mock provider
        class MockProvider:
            def generate_text(self, prompt): return "Mock Response"
            def generate_json(self, prompt): return {}
        agent.provider = MockProvider()
        
        # Mock _perform_search for speed
        async def mock_search(query, limit=None, status_callback=None):
            if status_callback: status_callback(f"🔎 Mock Search: {query}")
            return {"results": [{"url": "http://example.com", "title": "Mock Result"}]}
        
        agent._perform_search = mock_search
        
        print("✅ Agent initialized with mocks.")
    except Exception as e:
        print(f"❌ Failed to init agent: {e}")
        return

    # Strategy that triggers the agent
    print("▶️ Starting Mission...")
    strategy = {
        "strategy_name": "Test Async Mission",
        "mode": "conductor",
        "sequence": [
            {
                "type": "agent", 
                "agent": "RESEARCHER", 
                "task": "Test Query for Concurrency" 
            }
        ]
    }
    
    # We pass None as manager_agent because in this micro-test we aren't using the manager
    # BUT the engine calls manager_agent.run_mission if not in sequence mode.
    # IN sequence mode (which we are), it calls sub_agent logic directly.
    engine.start_mission(strategy, None) 
    
    # Wait and observe
    for i in range(10):
        time.sleep(1)
        if not engine.is_running:
            print("✅ Engine finished.")
            break
        print(f"⏳ Engine running... {i}s")
    else:
        print("⚠️ Engine timed out. Stopping...")
        engine.stop()
        
    print("\n📜 Engine Logs:")
    for log in engine.logs:
        print(log)
        
    # Check for specific success messages
    success = any("completed task (async)" in log for log in engine.logs)
    if success:
        print("\n✅ PASSED: Agent executed via think_async!")
    else:
        print("\n❌ FAILED: Did not see async completion log.")
        
    # Check for errors
    errors = any("RuntimeError" in log or "Error" in log or "Traceback" in log for log in engine.logs)
    if errors:
        print("❌ ERRORS FOUND IN LOGS!")
    else:
        print("✅ NO ERRORS in logs.")

if __name__ == "__main__":
    test_async_execution()
