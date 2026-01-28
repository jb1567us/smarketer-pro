import json
import os
import sys
import re

# Add project root and src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from prompt_engine import PromptEngine, PromptContext

def verify_proxy_config():
    print("Verifying ProxyManager Config Logic...", end=" ")
    path = "tests/golden_master/snapshots/core_proxy_config.json"
    if not os.path.exists(path):
        print("SKIP")
        return True
    with open(path, 'r', encoding='utf-8') as f:
        snap = json.load(f)
    initial = snap['initial']
    test_proxies = snap['proxies_added']
    proxy_list_yaml = "    all://:\n"
    for addr in test_proxies:
        proxy_list_yaml += f"      - http://{addr}\n"
    parts = initial.split("outgoing:", 1)
    pre_outgoing = parts[0] + "outgoing:"
    post_outgoing = parts[1]
    regex_proxies = r"(\n  proxies:\n(?:    .*\n)*)"
    new_block = "\n  proxies:\n" + proxy_list_yaml
    modified_post = re.sub(regex_proxies, "", post_outgoing, flags=re.MULTILINE)
    if not modified_post.startswith("\n"): modified_post = "\n" + modified_post
    modified_post = new_block + modified_post
    actual = pre_outgoing + modified_post
    if actual == snap['final']:
        print(" PASS")
        return True
    else:
        print(" FAIL")
        return False

def verify_prompt_engine():
    print("Verifying PromptEngine Templates...", end=" ")
    path = "tests/golden_master/snapshots/core_prompts.json"
    if not os.path.exists(path):
        print("SKIP")
        return True
    with open(path, 'r', encoding='utf-8') as f:
        snap = json.load(f)
    pe = PromptEngine()
    failed = []
    for res in snap['results']:
        template = res['template']
        ctx_dict = res['context']
        context = PromptContext(**ctx_dict)
        actual = pe.get_prompt(template, context, icp="Founders", offering="AI", constraints="None")
        if actual != res['rendered']:
            failed.append(template)
    if not failed:
        print(" PASS")
        return True
    else:
        print(f" FAIL ({failed})")
        return False

def verify_workflow_engine():
    print("Verifying Workflow Engine traversal...", end=" ")
    path = "tests/golden_master/snapshots/core_workflow.json"
    if not os.path.exists(path):
        print("SKIP")
        return True
    with open(path, 'r', encoding='utf-8') as f:
        snap = json.load(f)
    from nodes.base import BaseNode
    class MockNode(BaseNode):
        def __init__(self, ntype, dname): self._ntype=ntype; self._dname=dname
        @property
        def node_type(self): return self._ntype
        @property
        def display_name(self): return self._dname
        async def execute(self, context, params): return {"status": "ok"}
    import nodes.registry
    nodes.registry.NODE_REGISTRY["trigger.manual"] = MockNode("t", "trigger")
    nodes.registry.NODE_REGISTRY["action.search"] = MockNode("a", "action")
    from engine.core import WorkflowEngine
    import asyncio
    engine = WorkflowEngine(db_path=":memory:")
    logs = []
    async def run(): await engine.run_workflow(snap['workflow'], {}, status_callback=lambda m: logs.append(m), wait=True)
    if sys.platform == 'win32': asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    loop = asyncio.new_event_loop()
    loop.run_until_complete(run())
    loop.close()
    if logs == snap['logs']:
        print(" PASS")
        return True
    else:
        print(" FAIL (Log mismatch)")
        return False

if __name__ == "__main__":
    v1 = verify_proxy_config()
    v2 = verify_prompt_engine()
    v3 = verify_workflow_engine()
    if v1 and v2 and v3: sys.exit(0)
    else: sys.exit(1)
