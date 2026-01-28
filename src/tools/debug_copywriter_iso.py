import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Step 1: Importing BaseAgent")
try:
    from agents.base import BaseAgent
    print("Step 1: Success")
except Exception as e:
    print(f"Step 1 Failed: {e}")

print("Step 2: Importing json")
import json
print("Step 2: Success")

print("Step 3: Importing Copywriter module directly")
try:
    import agents.copywriter
    print("Step 3: Success")
except Exception as e:
    print(f"Step 3 Failed: {e}")
