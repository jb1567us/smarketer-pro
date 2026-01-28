import asyncio
import os
import sys
import json

# Add project root and src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from prompt_engine import PromptEngine, PromptContext
from engine.core import WorkflowEngine

def capture_prompt_engine():
    print("🎨 Capturing PromptEngine...")
    pe = PromptEngine()
    context = PromptContext(niche="SaaS", icp_role="CTO")
    templates = [
        "researcher/discovery_query_generator.j2",
        "copywriter/email_cold.j2",
        "manager/task_delegator.j2",
        "influencer/scout.j2"
    ]
    results = []
    for t in templates:
        rendered = pe.get_prompt(t, context, icp="Founders", offering="AI", constraints="None")
        results.append({"template": t, "context": context.to_dict(), "rendered": rendered})
    
    os.makedirs("tests/golden_master/snapshots", exist_ok=True)
    with open("tests/golden_master/snapshots/core_prompts.json", 'w', encoding='utf-8') as f:
        json.dump({"target": "prompt_engine", "results": results}, f, indent=2)
    print("  💾 Saved: core_prompts.json")

async def capture_workflow_engine():
    print("⚙️ Capturing Workflow Engine...")
    workflow = {
        "id": "master_snap",
        "nodes": [
            {"id": "n1", "type": "trigger.manual"},
            {"id": "n2", "type": "action.search", "params": {"query": "test"}}
        ],
        "edges": [{"source": "n1", "target": "n2"}]
    }
    
    from nodes.base import BaseNode
    class MockNode(BaseNode):
        def __init__(self, ntype, dname):
            self._ntype = ntype
            self._dname = dname
        @property
        def node_type(self): return self._ntype
        @property
        def display_name(self): return self._dname
        async def execute(self, context, params): return {"status": "ok"}
            
    import nodes.registry
    nodes.registry.NODE_REGISTRY["trigger.manual"] = MockNode("t", "trigger")
    nodes.registry.NODE_REGISTRY["action.search"] = MockNode("a", "action")

    engine = WorkflowEngine(db_path=":memory:")
    logs = []
    await engine.run_workflow(workflow, {}, status_callback=lambda m: logs.append(m), wait=True)
    
    with open("tests/golden_master/snapshots/core_workflow.json", 'w', encoding='utf-8') as f:
        json.dump({"target": "workflow_engine", "workflow": workflow, "logs": logs}, f, indent=2)
    print("  💾 Saved: core_workflow.json")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    capture_prompt_engine()
    asyncio.run(capture_workflow_engine())
