import json
import os
import sys
import glob

# Add project root and src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from scrapers.serp_logic import extract_serp_results

def run_verification():
    snapshot_dir = "tests/golden_master/snapshots"
    if not os.path.exists(snapshot_dir): return
    files = glob.glob(os.path.join(snapshot_dir, "serp_*.json"))
    passed = 0
    failed = 0
    for fpath in files:
        with open(fpath, 'r', encoding='utf-8') as f:
            snap = json.load(f)
        try:
            actual = extract_serp_results(snap['html'])
            if actual == snap['expected']:
                print(f"Testing {os.path.basename(fpath)}... PASS")
                passed += 1
            else:
                print(f"Testing {os.path.basename(fpath)}... FAIL")
                failed += 1
        except Exception as e:
            print(f" ERROR: {e}")
            failed += 1
    print(f"\nDirect Scraper Results: {passed} PASSED, {failed} FAILED.")
    if failed > 0: sys.exit(1)

if __name__ == "__main__":
    run_verification()
