import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from agents.social_listener import SocialListeningAgent
from llm import LLMFactory

# Mock the provider to avoid actual API calls during repro checking if needed, 
# but here we want to see the agent logic.
# The agent logic uses random mock data, so we don't even need a real LLM for that part, 
# although it uses LLM for analysis. 
# We'll just print the "raw" posts before analysis to confirm they come from the mock template.

async def main():
    agent = SocialListeningAgent()
    print("--- Searching via SearXNG ---")
    
    # We need to mock the provider for the analyze_signal part if we don't want to burn tokens or if no key is set.
    # However, let's try to run it 'as is'. If it fails on LLM, we at least know search worked if we add logging or print debugging.
    # Actually, let's just inspect the results.

    try:
        # Use a very broad query to check if ANY results come back
        results = await agent.listen_for_keywords(["python"], platforms=["twitter"])
        print(f"Found {len(results)} signals.")
        for p in results:
            print(f"Content: {p['content']}")
            print(f"URL: {p['url']}")
            print("-" * 20)
    except Exception as e:
        print(f"Agent execution failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
