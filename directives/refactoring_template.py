"""
REFACTORING TEMPLATE
--------------------
Usage:
1. Copy this file to `directives/refactor_sessions/refactor_my_task_name.py`.
2. Configure the 'TARGET CONFIGURATION' section.
3. Run `python directives/refactor_sessions/refactor_my_task_name.py --record`.
4. Perform your refactoring.
5. Run `python directives/refactor_sessions/refactor_my_task_name.py --verify`.
"""

import sys
import os

# Add parent directories to path to allow importing refactor_tools and src
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir)) # Assumes directives/refactor_sessions/script.py layout
if os.path.basename(current_dir) == "directives": # If running directly in directives/
    project_root = os.path.dirname(current_dir)

sys.path.append(project_root)
sys.path.append(os.path.join(project_root, "directives"))

from refactor_tools import GoldenMaster, LegacyKeeper

# ==========================================
# TARGET CONFIGURATION
# ==========================================

# 1. Import the function/component you want to refactor
# from src.my_module import my_complex_function as target_function
target_function = None  # REPLACE THIS

# 2. Define the inputs you want to test
# Dictionary of arguments to pass to the function.
# TIP: If the function is slow (API/DB), consider passing mock objects here!
test_inputs = [
    # {"arg1": "value1", "arg2": 10},
    # {"arg1": "value2", "arg2": 20},
]

# 3. Name your snapshot
snapshot_name = "snapshot_v1" 

# ==========================================
# EXECUTION
# ==========================================

def main():
    if target_function is None:
        print("ERROR: You must configure 'target_function' in the script.")
        return

    if "--record" in sys.argv:
        print(f"🎥 Recording behavior for {snapshot_name}...")
        gm = GoldenMaster()
        gm.record(
            func=target_function,
            inputs=test_inputs,
            snapshot_name=snapshot_name
        )
        print("✅ Recording complete. Now go refactor!")

    elif "--verify" in sys.argv:
        print(f"🔍 Verifying behavior for {snapshot_name}...")
        gm = GoldenMaster()
        gm.verify(
            func=target_function,
            snapshot_name=snapshot_name
        )
        
        # Optional: Log what changed if verification passes (or fails safely)
        # keeper = LegacyKeeper()
        # keeper.log_behavior("REFACTOR_COMPLETE", "Refactored X to use Y")
        
    else:
        print("Usage:")
        print("  python refactor_template.py --record  (BEFORE changes)")
        print("  python refactor_template.py --verify  (AFTER changes)")

if __name__ == "__main__":
    main()
