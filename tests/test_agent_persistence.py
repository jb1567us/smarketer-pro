import sys
import os
import json
import sqlite3
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import init_db, get_connection, get_agent_work, clear_all_leads
from agents.base import BaseAgent

# Mock provider for testing
class MockProvider:
    def generate_text(self, prompt):
        return "Mocked text response"
    def generate_json(self, prompt):
        return {"mock": "data", "status": "success"}

# Mock Agent
class TestAgent(BaseAgent):
    def __init__(self):
        super().__init__(role="Test Agent", goal="Testing persistence", provider=MockProvider())
    
    def think(self, context):
        result = "Thinking about " + context
        self.save_work(result, artifact_type="text", metadata={"context": context})
        return result

def test_persistence():
    print("Initializing Database...")
    init_db()
    
    # 1. Test manual save from BaseAgent subclass
    agent = TestAgent()
    print("Running TestAgent...")
    output = agent.think("Unit Testing")
    print(f"Agent Output: {output}")
    
    # Verify in DB
    print("Verifying in Database...")
    works = get_agent_work(agent_role="Test Agent", limit=1)
    
    if not works:
        print("FAIL: No work found for Test Agent")
        return False
        
    latest_work = works[0]
    print(f"Retrieved Work: {latest_work}")
    
    if latest_work['content'] == "Thinking about Unit Testing" and latest_work['artifact_type'] == 'text':
        print("SUCCESS: Content matches")
    else:
        print("FAIL: Content mismatch")
        return False
        
    # Check Metadata
    meta = json.loads(latest_work['metadata'])
    if meta.get('context') == "Unit Testing":
        print("SUCCESS: Metadata matches")
    else:
        print("FAIL: Metadata mismatch")
        return False

    return True

if __name__ == "__main__":
    try:
        if test_persistence():
            print("\nAll Tests Passed!")
            sys.exit(0)
        else:
            print("\nTests Failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
