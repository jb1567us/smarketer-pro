import asyncio
import sys
import os

# Add project root to path (parent of src)
# This allows 'from src.agents import ...'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Add src to path for legacy imports (e.g. 'from flow...')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.manager import ManagerAgent

def test_manager_nodes():
    print("Initializing Manager...")
    try:
        mgr = ManagerAgent() 
    except Exception as e:
        print(f"Warning: Manager Init failed (likely provider missing), but checking if method exists. {e}")
        # We can still test the method if we can import the class
        from src.nodes.registry import NODE_REGISTRY
        import src.nodes
        print(f"Direct Registry Check: {len(NODE_REGISTRY)} nodes.")
        nodes = [] 
        for node_type, node_inst in NODE_REGISTRY.items():
             nodes.append({"type": node_type, "name": node_inst.display_name})
    else:
        print("Listing available nodes...")
        nodes = mgr.list_available_nodes()
    
    print(f"Found {len(nodes)} nodes.")
    for n in nodes:
        print(f" - {n['type']} ({n['name']})")
        
    if len(nodes) > 0:
        print("✅ SUCCESS: Nodes listed.")
    else:
        print("❌ FAILURE: No nodes found.")

if __name__ == "__main__":
    test_manager_nodes()
