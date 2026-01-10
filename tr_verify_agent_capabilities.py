import sys
import os
import json
import time

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from agents.base import BaseAgent
from agents.custom_agent import CustomAgent
from database import get_agent_work_products

def test_base_agent_capabilities():
    print("\n--- Testing BaseAgent Capabilities ---")
    
    # 1. Setup
    original_agent = BaseAgent(role="Tester", goal="Verify Code")
    original_agent.backstory = "I am a test agent."
    
    # 2. Export
    print("Exporting data...")
    data = original_agent.export_data()
    print(f"Exported Data: {json.dumps(data, indent=2)}")
    
    assert data['role'] == "Tester"
    assert data['goal'] == "Verify Code"
    assert data['backstory'] == "I am a test agent."
    
    # 3. Import
    print("Importing into new agent...")
    new_agent = BaseAgent(role="Newbie", goal="Learn")
    new_agent.import_data(data)
    
    assert new_agent.role == "Tester"
    assert new_agent.goal == "Verify Code"
    assert new_agent.backstory == "I am a test agent."
    print("Import verification passed!")
    
    # 4. Save Work
    print("Saving work product...")
    content = "This is a test work product."
    metadata = {"test_run": "123", "input_task": "Test Saving"}
    
    product_id = original_agent.save_work(content, metadata=metadata)
    print(f"Saved work product ID: {product_id}")
    
    assert product_id is not None
    
    # Verify DB content
    products = get_agent_work_products(agent_role="Tester", limit=1)
    if products:
        saved_product = products[0]
        print(f"Retrieved Product: {saved_product['output_content']}")
        assert saved_product['output_content'] == content
        # Check if agent_state was auto-saved in metadata
        saved_meta = json.loads(saved_product['metadata'])
        assert "agent_state" in saved_meta
        assert saved_meta['agent_state']['role'] == "Tester"
        print("DB verification passed!")
    else:
        print("FAILED to retrieve work product!")

def test_custom_agent_capabilities():
    print("\n--- Testing CustomAgent Capabilities ---")
    
    # 1. Setup
    original_agent = CustomAgent(name="MyCustomBot", role="Specialist", goal="Do special things", system_prompt="Be special.")
    
    # 2. Export
    print("Exporting data...")
    data = original_agent.export_data()
    print(f"Exported Data: {json.dumps(data, indent=2)}")
    
    assert data['role'] == "Specialist"
    assert data['name'] == "MyCustomBot"
    assert data['system_prompt'] == "Be special."
    
    # 3. Import
    print("Importing into new agent...")
    new_agent = CustomAgent(name="OldBot", role="Generalist", goal="Exist")
    new_agent.import_data(data)
    
    assert new_agent.role == "Specialist"
    assert new_agent.name == "MyCustomBot"
    assert new_agent.system_prompt == "Be special."
    print("CustomAgent Import verification passed!")

if __name__ == "__main__":
    try:
        test_base_agent_capabilities()
        test_custom_agent_capabilities()
        print("\nAll tests passed successfully.")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
