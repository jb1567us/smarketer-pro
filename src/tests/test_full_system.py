import asyncio
import os
import sys

# Ensure src is in path to satisfy legacy internal imports (e.g. 'import llm')
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

# Ensure BOTH project root and src are in path to handle mixed import styles
project_root = os.getcwd() # Should be c:\sandbox\b2b_outreach_tool
src_path = os.path.join(project_root, 'src')

if project_root not in sys.path:
    sys.path.append(project_root)
if src_path not in sys.path:
    # Append to end to fallback to legacy if not found in root
    sys.path.append(src_path)

# Use legacy import style which is more common in this existing codebase
from agents.manager import ManagerAgent
from engine.core import WorkflowEngine
import nodes.domain # auto-register

async def run_full_system_test():
    print("🚀 STARTING PHASE 4: FULL SYSTEM TEST")
    
    # 1. Initialize Manager
    print("\n[1] Initializing Manager Agent...")
    manager = ManagerAgent() # In real app, provider is injected
    
    # 2. Design Workflow
    goal = "Find AI startups in San Francisco and email them a hello message."
    print(f"\n[2] Asking Manager to DESIGN workflow for goal: '{goal}'")
    
    design_result = manager.design_workflow(
        goal, 
        nodes_description="Use 'domain.search' to find companies, 'domain.enrich' to analyze, and 'domain.email' to contact. Use 'core.if' to filter results."
    )
    
    if "error" in design_result:
        print(f"❌ Design Failed: {design_result['error']}")
        return

    workflow_file = design_result['file']
    print(f"✅ Workflow Designed! Saved to: {workflow_file}")
    
    # 3. Inspect Design (Optional Print)
    import json
    with open(workflow_file, 'r') as f:
        wf_data = json.load(f)
        print(f"   Nodes: {[n['type'] for n in wf_data.get('nodes', [])]}")

    # 4. Execute Workflow
    workflow_name = os.path.basename(workflow_file).replace('.json', '')
    print(f"\n[3] Asking Manager to EXECUTE workflow: '{workflow_name}'")
    
    # We trigger the execution via the manager's capability
    exec_result = await manager.execute_workflow(workflow_name, payload={"trigger_data": "test_run"})
    
    if "error" in exec_result:
        print(f"❌ Execution Trigger Failed: {exec_result['error']}")
        return
        
    execution_id = exec_result['execution_id']
    print(f"✅ Execution Started! ID: {execution_id}")
    
    # 5. Monitor Status (Simple Polling)
    print("\n[4] Monitoring Execution (Polling DB)...")
    engine = WorkflowEngine()
    
    for _ in range(10): # Wait up to 10 seconds
        status = engine.get_status(execution_id)
        print(f"   Status: {status['status']} (Steps: {len(status.get('steps', {}))})")
        if status['status'] in ['COMPLETED', 'FAILED']:
             break
        await asyncio.sleep(1)
        
    final_status = engine.get_status(execution_id)
    print(f"\n🏁 FINAL RESULT: {final_status['status']}")
    if final_status['status'] == 'FAILED':
        print(f"   Error: {final_status.get('error')}")
    else:
        print("   Success! Check 'campaign_events' or logs for email delivery.")

if __name__ == "__main__":
    asyncio.run(run_full_system_test())
