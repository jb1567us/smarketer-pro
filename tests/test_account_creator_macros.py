import asyncio
import os
import sys
import json
import sqlite3

# Appends src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agents.account_creator import AccountCreatorAgent
from database import init_db, get_registration_tasks, save_registration_macro, get_registration_macro

async def test_fallback_and_macros():
    print("Starting Account Creator Fallback Verification...")
    
    # 1. Initialize DB
    init_db()
    
    # 2. Mock Config
    cpanel_config = {
        'url': 'https://mock.cpanel.com',
        'user': 'mock_user',
        'token': 'mock_token',
        'domain': 'mock.com'
    }
    
    agent = AccountCreatorAgent(cpanel_config)
    
    # 3. Test Task Creation on Failure
    # We'll point it at a non-existent URL or one that clearly fails AI detection
    print("\nStep 3: Testing Task Creation on Failure...")
    # Mocking create_email_account to avoid actual cPanel calls
    agent.cpanel.create_email_account = lambda e, p: {'status': 'success'}
    
    result = await agent.create_account(
        "MockPlatform", 
        "http://example.com/register", 
        account_details={'username': 'testuser'}
    )
    print(f"Result: {result}")
    
    tasks = get_registration_tasks()
    found = any(t['platform'] == "MockPlatform" for t in tasks)
    if found:
        print("OK: Task successfully created in registration_tasks.")
    else:
        print("FAIL: Task NOT created.")

    # 4. Test Macro Saving
    print("\nStep 4: Testing Macro Saving...")
    steps = [
        {'type': 'change', 'selector': '#email', 'value': '{email}'},
        {'type': 'click', 'selector': '#submit'}
    ]
    save_registration_macro("MockPlatform", steps)
    
    macro = get_registration_macro("MockPlatform")
    if macro and json.loads(macro['steps']) == steps:
        print("OK: Macro successfully saved.")
    else:
        print("FAIL: Macro NOT saved correctly.")

    # 5. Test Macro Replay (via mock or logic check)
    print("\nStep 5: Verifying Macro Replay logic exists in Agent...")
    if hasattr(agent, '_replay_macro'):
        print("OK: Agent has _replay_macro method.")
    else:
        print("FAIL: Agent MISSING _replay_macro method.")

    print("\nVerification Complete.")

if __name__ == "__main__":
    asyncio.run(test_fallback_and_macros())
