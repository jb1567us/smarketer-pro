import os
import sys
import json

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from agents.manager import ManagerAgent

def test_manager_guardrail():
    print("Starting Quick Verification of Manager Agent Guardrails...")
    
    agent = ManagerAgent()
    
    test_inputs = [
        "build a demo wp site on lookoverhere.xyz/wp-auto-demo create the folder and install there and make a mini site about malti-pom dogs",
        "install wordpress on test.com/blog",
        "create a new site on mydomain.org/site"
    ]
    
    all_passed = True
    
    for i, user_input in enumerate(test_inputs):
        print(f"\n--- Test Case {i+1}: '{user_input}' ---")
        
        # We use think() which now has the aggressive interceptor
        response = agent.think(user_input)
        
        tool = response.get("tool")
        params = response.get("params", {})
        
        print(f"Detected Tool: {tool}")
        print(f"Detected Params: {json.dumps(params, indent=2)}")
        
        if tool == "build_wordpress_site":
            print("PASSED: Correct tool triggered.")
            # Verify extraction
            if "domain" in params and "directory" in params:
                print(f"Detected Domain: {params['domain']}")
                print(f"Detected Directory: {params['directory']}")
            else:
                 print("FAILED: Missing domain/directory parameters.")
                 all_passed = False
        else:
            print(f"FAILED: Expected 'build_wordpress_site', but got '{tool}'.")
            all_passed = False
            
    if all_passed:
        print("\nALL GUARDRAIL TESTS PASSED!")
    else:
        print("\nSOME TESTS FAILED. Check the output above.")

if __name__ == "__main__":
    test_manager_guardrail()
