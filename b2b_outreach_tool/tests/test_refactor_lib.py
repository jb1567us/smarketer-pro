import sys
import os

# Add root to path so we can import 'refactor_tools'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from refactor_tools import GoldenMaster, LegacyKeeper, PreservationChecklist

def test_add(a, b):
    # Original behavior
    return a + b

def test_add_buggy(a, b):
    # Modified behavior (bug)
    return a + b + 1

def run_verification():
    print("🚀 Starting Refactor Tools Verification...")
    
    # 1. Test Golden Master
    gm = GoldenMaster(snapshot_dir="test_snapshots")
    inputs = [{"a": 1, "b": 2}, {"a": 10, "b": 20}]
    
    # Record
    snap_path = gm.record(test_add, inputs, "test_add_v1")
    print(f"✅ Recorded snapshot to {snap_path}")
    
    # Verify Success
    success = gm.verify(test_add, "test_add_v1")
    if success:
        print("✅ Verification Passed (Expected)")
    else:
        print("❌ Verification Failed (Unexpected)")

    # Verify Failure
    print("⚠️ Testing verification failure (this SHOULD fail)...")
    fail_compat = gm.verify(test_add_buggy, "test_add_v1")
    if not fail_compat:
        print("✅ Verification Correctly Failed (Expected)")
    else:
        print("❌ Verification Passed (Unexpected - should have failed)")

    # 2. Test Legacy Keeper
    keeper = LegacyKeeper(archive_dir="test_legacy")
    arch_path = keeper.archive_code("test_add_function", "def test_add(a,b): return a+b", "Testing archive")
    print(f"✅ Archived code to {arch_path}")
    
    # 3. Test Preservation
    checklist = PreservationChecklist()
    checklist.add_item("Keep adding numbers correctly")
    check_path = "test_checklist.md"
    checklist.save_to_file(check_path)
    print(f"✅ Saved checklist to {check_path}")

if __name__ == "__main__":
    run_verification()
