import asyncio
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))
from agents.proxy_agent import ProxyAgent

async def test_harvest():
    agent = ProxyAgent()
    print("Testing harvesting...")
    # Override sources to just one fast source for testing
    agent.sources = ["https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"]
    
    proxies = await agent.harvest_all()
    print(f"Harvested {len(proxies)} proxies.")
    
    print("Testing validation on first 5...")
    to_test = set(list(proxies)[:5])
    elite = await agent.validate_proxies(to_test)
    print(f"Found {len(elite)} elite proxies from test batch.")

if __name__ == "__main__":
    asyncio.run(test_harvest())
