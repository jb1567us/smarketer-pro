import sys
import os
import time

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from database import init_db, get_agent_work_products, save_agent_work_product
from agents.base import BaseAgent

def verify_work_product():
    print("1. Initializing DB...")
    init_db()
    
    print("2. Testing direct DB save...")
    save_agent_work_product(
        agent_role="Test Agent",
        input_task="Test Task",
        output_content="Test Content",
        tags=["test"]
    )
    
    products = get_agent_work_products("Test Agent")
    if products and products[0]['output_content'] == "Test Content":
        print("   -> Success: Direct DB save worked.")
    else:
        print("   -> FAIL: Direct DB save failed.")
        return

    print("3. Testing BaseAgent save...")
    agent = BaseAgent(role="Verification Agent", goal="Verify Storage")
    agent.save_work_product("Agent Content", "Agent Task", tags=["agent_test"])
    
    products = get_agent_work_products("Verification Agent")
    if products and products[0]['output_content'] == "Agent Content":
        print("   -> Success: BaseAgent save worked.")
    else:
        print("   -> FAIL: BaseAgent save failed.")
        return

    print("Verification Complete: All systems nominal.")

if __name__ == "__main__":
    verify_work_product()
