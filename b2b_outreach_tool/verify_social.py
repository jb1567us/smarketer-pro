import asyncio
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))
from agents.social_listener import SocialListeningAgent

async def test_social_listening():
    agent = SocialListeningAgent()
    
    print("--- 1. Testing Listening Simulation ---")
    keywords = ["CRM for startups", "marketing automation issues"]
    signals = await agent.listen_for_keywords(keywords)
    
    print(f"Found {len(signals)} signals.")
    for s in signals[:2]:
        print(f"\nUser: {s['user']} ({s['platform']})")
        print(f"Content: {s['content']}")
        print(f"Intent Score: {s['analysis'].get('intent_score')}")
        print(f"Classification: {s['analysis'].get('classification')}")

    print("\n--- 2. Testing Reply Generation ---")
    if signals:
        target = signals[0]
        reply = agent.generate_reply(target['content'], target['analysis'].get('suggested_reply_angle'))
        print(f"Generated Reply: {reply}")

if __name__ == "__main__":
    asyncio.run(test_social_listening())
