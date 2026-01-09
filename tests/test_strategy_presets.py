import sys
import os
import sqlite3
import time

# Ensure src is in path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from database import init_db, save_strategy_preset, get_strategy_presets, get_strategy_preset, delete_strategy_preset, get_connection
from agents.pm import ProductManagerAgent
from unittest.mock import MagicMock

def test_database_operations():
    print("Testing Database Operations...")
    init_db() # Ensure table exists
    
    # Clean up any previous test data
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM strategy_presets WHERE name = 'Test Preset'")
    conn.commit()
    conn.close()

    # Test Save
    preset_id = save_strategy_preset("Test Preset", "A test description", "Test instructions for {niche}")
    print(f"Saved Preset ID: {preset_id}")
    assert preset_id is not None

    # Test Get All
    presets = get_strategy_presets()
    print(f"Found {len(presets)} presets.")
    found = False
    for p in presets:
        if p['id'] == preset_id:
            found = True
            assert p['name'] == "Test Preset"
            assert p['instruction_template'] == "Test instructions for {niche}"
            break
    assert found

    # Test Get Single
    p = get_strategy_preset(preset_id)
    assert p['name'] == "Test Preset"

    # Test Delete
    delete_strategy_preset(preset_id)
    p_after = get_strategy_preset(preset_id)
    assert p_after is None
    print("Database operations verified!")

def test_agent_logic():
    print("\nTesting Agent Logic...")
    agent = ProductManagerAgent()
    
    # Mock the provider to avoid real API calls
    agent.provider = MagicMock()
    agent.provider.generate_json.return_value = {"strategy_name": "Mock Strategy"}

    # Test Default
    agent.generate_campaign_strategy("Generic Context", niche="General")
    args, _ = agent.provider.generate_json.call_args
    assert "Develop a high-level outreach strategy" in args[0]
    
    # Test Custom
    custom_template = "This is a custom strategy for {niche} with context {product_context}."
    agent.generate_campaign_strategy("Generic Context", niche="SaaS", instruction_template=custom_template)
    args, _ = agent.provider.generate_json.call_args
    assert "This is a custom strategy for SaaS with context Generic Context." in args[0]
    print("Agent logic verified!")

if __name__ == "__main__":
    test_database_operations()
    test_agent_logic()
