import asyncio
from agents.wordpress import WordPressAgent
import json

async def test_wp_agent():
    print("Testing WordPressAgent...")
    agent = WordPressAgent()
    
    # 1. Test Install Config Generation
    print("\n--- Test 1: Install Config ---")
    config = agent.generate_install_config("test_wp")
    if "image: wordpress:latest" in config:
        print("✅ Config generation successful.")
    else:
        print("❌ Config generation failed.")

    # 2. Test think()
    print("\n--- Test 2: think() ---")
    thoughts = agent.think("How do I install WordPress?")
    print(f"Agent thoughts: {thoughts[:100]}...")
    if thoughts:
        print("✅ think() successful.")
    else:
        print("❌ think() failed.")

    print("\nVerification complete.")

if __name__ == "__main__":
    asyncio.run(test_wp_agent())
