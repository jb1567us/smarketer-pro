import asyncio
import os
import sys
import sqlite3
import json

# Add src to path
# Add project root to path
sys.path.append(os.getcwd())

from engine.core import WorkflowEngine
from engine.loader import WorkflowLoader
import nodes # Triggers registration


async def test_engine():
    print("🚀 Starting Engine Verification...")
    
    # 1. Setup
    engine = WorkflowEngine("test_workflow.db")
    
    # Clean DB for test
    if os.path.exists("test_workflow.db"):
        os.remove("test_workflow.db")
        engine._init_db()

    # 2. Load Workflow
    cwd = os.getcwd()
    workflow_path = os.path.join(cwd, "src", "workflows", "test_workflow.json")
    print(f"📂 Loading workflow from: {workflow_path}")
    
    workflow_def = WorkflowLoader.load_from_file(workflow_path)
    
    # 3. Execution
    payload = {"lead": {"name": "Test Company", "score": 90}}
    print(f"▶️  Running Workflow with payload: {payload}")
    
    execution_id = await engine.run_workflow(workflow_def, payload)
    print(f"✅ Execution ID: {execution_id}")
    
    # Wait for async background task (Simulate main loop waiting)
    print("⏳ Waiting for execution to finish...")
    await asyncio.sleep(2) 
    
    # 4. Verify DB
    conn = sqlite3.connect("test_workflow.db")
    cursor = conn.cursor()
    
    print("\n--- Execution Status ---")
    cursor.execute("SELECT status, start_time, end_time, error_message FROM workflow_executions WHERE execution_id=?", (execution_id,))
    row = cursor.fetchone()
    if row:
        print(f"Status: {row[0]}")
        print(f"Start:  {row[1]}")
        print(f"End:    {row[2]}")
        if row[3]:
            print(f"Error:  {row[3]}")
    else:
        print("❌ Execution record not found!")

    print("\n--- Step Logs ---")
    cursor.execute("SELECT step_id, node_type, output_json FROM step_logs WHERE execution_id=?", (execution_id,))
    logs = cursor.fetchall()
    for log in logs:
        print(f"Step: {log[0]} | Type: {log[1]} | Output: {log[2]}")
        
    conn.close()
    
    # Cleanup
    if os.path.exists("test_workflow.db"):
        os.remove("test_workflow.db")

if __name__ == "__main__":
    asyncio.run(test_engine())
