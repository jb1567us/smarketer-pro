import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agents.image_agent import ImageGenAgent

def test_image_gen():
    print("=== Image Generation Agent Test ===")
    try:
        agent = ImageGenAgent()
    except Exception as e:
        print(f"❌ Failed to initialize ImageGenAgent: {e}")
        return
    
    prompt = "A high-tech sleek office with holographic displays, cinematic lighting, 8k"
    print(f"Input Prompt: {prompt}")
    
    result = agent.think(prompt)
    
    if result.get('status') == 'success':
        print("\n✅ Image Generation SUCCESS!")
        print(f"Enhanced Prompt: {result.get('enhanced_prompt')}")
        print(f"Image URL: {result.get('image_url')}")
    else:
        print("\n❌ Image Generation FAILED.")
        print(f"Error: {result.get('error')}")

if __name__ == "__main__":
    test_image_gen()
