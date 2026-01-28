import json
import os
import sys

# Add project root and src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from social_scraper import parse_social_stats

def verify_parsing():
    print("Verifying Social Stats Parsing...", end=" ")
    path = "tests/golden_master/snapshots/social_parsing.json"
    if not os.path.exists(path):
        print("SKIP")
        return True
    with open(path, 'r', encoding='utf-8') as f:
        snap = json.load(f)
    failed_cases = []
    for case in snap['results']:
        actual = parse_social_stats(case['input'])
        if actual != case['output']:
            failed_cases.append((case['input'], case['output'], actual))
    if not failed_cases:
        print(" PASS")
        return True
    else:
        print(f" FAIL ({len(failed_cases)} cases)")
        return False

def verify_html():
    print("Verifying Social HTML Extraction...", end=" ")
    path = "tests/golden_master/snapshots/social_html.json"
    if not os.path.exists(path):
        print("SKIP")
        return True
    with open(path, 'r', encoding='utf-8') as f:
        snap = json.load(f)
    from bs4 import BeautifulSoup
    failed_cases = []
    for sample in snap['samples']:
        soup = BeautifulSoup(sample['html_input'], 'html.parser')
        meta = soup.find("meta", property="og:description")
        desc = meta.get("content", "") if meta else ""
        stats = parse_social_stats(desc)
        if stats != sample['final_stats']:
            failed_cases.append((sample['platform'], sample['final_stats'], stats))
    if not failed_cases:
        print(" PASS")
        return True
    else:
        print(f" FAIL ({len(failed_cases)} cases)")
        return False

if __name__ == "__main__":
    v1 = verify_parsing()
    v2 = verify_html()
    if v1 and v2:
        print("All Social Verifications: PASSED")
        sys.exit(0)
    else:
        print("Some Social Verifications: FAILED")
        sys.exit(1)
