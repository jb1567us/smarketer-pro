
import asyncio
import sys
import os

# Ensure src is in path logic
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
sys.path.append(current_dir)

from agents.account_creator import AccountCreatorAgent
from config import get_cpanel_config
from video_gen.auth_configs import VIDEO_AUTH_CONFIGS
from proxy_manager import proxy_manager

async def test_kling():
    print("🚀 Starting Kling Registration Test (Retry)...")
    
    # 1. Config
    cp_conf = get_cpanel_config()
    if not cp_conf or not cp_conf.get('url'):
        print("❌ cPanel config missing.")
        return

    # 2. Proxy
    print("🔎 Fetching Proxy...")
    # Using a verified elite proxy from the recent harvester logs to proceed immediately
    proxy = "http://34.44.49.215:80"
    
    if not proxy:
        print("❌ No proxies available. Aborting.")
        return
        
    print(f"✅ Using Proxy: {proxy}")

    # 3. Agent
    # explicitly pass config to ensure domain is correct if missed in env
    agent = AccountCreatorAgent(cp_conf)
    
    kling_conf = VIDEO_AUTH_CONFIGS.get('kling')
    url = kling_conf['registration_url']
    print(f"🌍 Target URL: {url}")
    
    # 4. Run
    print("🤖 Agent attempting registration...")
    
    result = await agent.create_account("KlingUser", url, proxy=proxy)
    
    print("-" * 30)
    print(f"RESULT: {result}")
    print("-" * 30)

if __name__ == "__main__":
    asyncio.run(test_kling())
