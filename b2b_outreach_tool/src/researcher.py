import os
import json
import time
from llm import LLMFactory

def research_niche(niche):
    """
    Analyzes a niche using LLM to identify top pain points.
    Returns a list of dicts: [{'title': '...', 'description': '...'}]
    """
    prompt = f"""
    Act as a B2B Market Researcher.
    Analyze the "{niche}" industry.
    Identify the TOP 5 most critical pain points, challenges, or "bleeding neck" problems faced by businesses in this niche right now.
    
    Return a list of JSON objects. Each object must have:
    - "title": A short, punchy title for the pain point (3-7 words).
    - "description": A 2-sentence explanation of why this is a problem and its business impact.
    """

    print(f"Researching pain points for: {niche}...")

    provider = LLMFactory.get_provider()
    result = provider.generate_json(prompt)
    
    if result:
         # Handle case where API might wrap list in a dict key
        if isinstance(result, dict) and 'pain_points' in result:
            return result['pain_points']
        elif isinstance(result, list):
            return result
            
    print("Researcher failed to get valid JSON results.")
    return []

if __name__ == "__main__":
    # Test
    from dotenv import load_dotenv
    load_dotenv()
    points = research_niche("Interior Design Firms")
    print(json.dumps(points, indent=2))
