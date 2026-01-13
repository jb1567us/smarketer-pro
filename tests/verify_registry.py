import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

def test_registry():
    print("Testing Node Registry...")
    
    # Initally empty
    from src.nodes.registry import NODE_REGISTRY
    print(f"Initial Registry Keys: {list(NODE_REGISTRY.keys())}")
    
    # Import manager_ui which should trigger the registration
    print("Importing manager_ui...")
    try:
        import src.ui.manager_ui
    except Exception as e:
        print(f"Import failed (expected in CLI due to streamlit deps, but we check registry): {e}")
        # Note: Importing manager_ui might fail because of 'streamlit' not being in context, 
        # but the side-effect imports should happen before that if placed correctly.
        # Actually, let's just import the node directly to see if that works as a fallback test.
    
    # Re-check registry
    print(f"Registry Keys after import: {list(NODE_REGISTRY.keys())}")
    
    if "domain.wordpress" in NODE_REGISTRY:
        print("✅ SUCCESS: 'domain.wordpress' found in registry.")
    else:
        print("❌ FAILURE: 'domain.wordpress' NOT found.")

if __name__ == "__main__":
    test_registry()
