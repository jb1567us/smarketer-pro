import sys
import os
import asyncio
import json

# Appends src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agents import ManagerAgent, ResearcherAgent
from config import config

async def test_limits():
    print("--- Testing Search Limits ---")
    
    # Check config
    print(f"Config max_results: {config['search'].get('max_results')}")
    if config['search'].get('max_results') > 50:
        print("FAIL: config max_results still too high")
    else:
        print("PASS: config max_results is safe")

    manager = ManagerAgent()
    researcher = ResearcherAgent()

    # Test 1: Researcher Direct Limit
    print("\nTesting Researcher Direct Limit (limit=2)...")
    res1 = await researcher.gather_intel({"query": "SEO agencies in Chicago", "limit": 2})
    count1 = len(res1.get('results', []))
    print(f"Found {count1} results.")
    if count1 > 2:
        print(f"FAIL: Researcher returned {count1} results, expected max 2")
    else:
        print("PASS: Researcher respected limit")

    # Test 2: Manager Mission Limit extraction
    print("\nTesting Manager Mission Limit extraction ('Find 1 lead')...")
    # Mocking the mission to avoid full loop if possible, or just running it for 1
    # Since it's a mission, it might take a moment.
    report = await manager.run_mission("Find 1 lead for a bakery in Paris")
    count2 = len(report.get('leads', []))
    print(f"Manager found {count2} leads.")
    if count2 > 1:
        print(f"FAIL: Manager returned {count2} leads, expected max 1")
    else:
        print("PASS: Manager respected limit")

if __name__ == "__main__":
    asyncio.run(test_limits())
