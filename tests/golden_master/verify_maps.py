import json
import os
import sys
import glob

# Add src path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
from maps.logic import parse_list_item, parse_detail_page

def normalize_data(data):
    d = {k: v for k, v in data.items() if k in ["business_name", "website", "phone"]}
    if "phone" in d and d["phone"] and d["phone"].lower().startswith("phone:"):
         d["phone"] = d["phone"].split(":", 1)[1].strip()
    return d

def run_verification():
    snapshot_dir = "tests/golden_master/snapshots"
    if not os.path.exists(snapshot_dir):
        return
    files = glob.glob(os.path.join(snapshot_dir, "*.json"))
    passed = 0
    failed = 0
    for fpath in files:
        with open(fpath, 'r', encoding='utf-8') as f:
            snap = json.load(f)
        if snap.get('type') not in ['maps_list_item', 'maps_detail_page']:
            continue
        try:
            expected = normalize_data(snap['expected'])
            if snap['type'] == 'maps_list_item':
                actual = parse_list_item(snap['html'])
            else:
                actual = parse_detail_page(snap['html'])
            active_actual = normalize_data(actual)
            if active_actual == expected:
                print(f"Testing {os.path.basename(fpath)}... PASS")
                passed += 1
            else:
                print(f"Testing {os.path.basename(fpath)}... FAIL")
                failed += 1
        except Exception as e:
            print(f" ERROR: {e}")
            failed += 1
    print(f"\nResults: {passed} PASSED, {failed} FAILED.")
    if failed > 0: sys.exit(1)

if __name__ == "__main__":
    run_verification()
