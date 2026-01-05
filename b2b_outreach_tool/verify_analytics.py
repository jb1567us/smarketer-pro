import asyncio
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))
from analytics_bridge import analytics_bridge
from agents.copywriter import CopywriterAgent

async def test_analytics_feedback():
    print("--- 1. Testing Analytics Bridge ---")
    pixel = analytics_bridge.generate_tracking_pixel("camp_123", "lead_456")
    print(f"Generated Pixel: {pixel}")
    
    # Mock aggregation
    print("Simulating event recording...")
    analytics_bridge.record_event("open", "camp_123", "lead_456")
    
    print("\n--- 2. Testing Optimization Loop ---")
    agent = CopywriterAgent()
    
    # Simulate a failing campaign
    bad_stats = {"open_rate": 0.12, "click_rate": 0.01}
    current_copy = {
        "subject": "Meeting request",
        "body": "Can we meet next week?"
    }
    
    print(f"Analyzing stats: {bad_stats}")
    print("AI Optimizing...")
    res = agent.optimize_campaign(current_copy, bad_stats)
    
    print(f"Diagnosis: {res.get('diagnosis')}")
    print("Variants:")
    for v in res.get('optimized_variants', []):
        print(f" - {v}")

if __name__ == "__main__":
    asyncio.run(test_analytics_feedback())
