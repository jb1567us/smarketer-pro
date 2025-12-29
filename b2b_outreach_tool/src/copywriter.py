import os
import json
import time
from llm import LLMFactory

def generate_campaign_sequence(niche, pain_point, product_name, product_description):
    """
    Generates a 3-email sequence (Intro, Value, Call-to-Action) based on a pain point using LLM.
    Returns: List of dicts [{'stage': 'intro', 'subject': '...', 'body': '...'}, ...]
    """
    
    prompt = f"""
    Act as a world-class B2B Copywriter.
    
    Context:
    - Target Niche: {niche}
    - Key Pain Point: {pain_point['title']} ({pain_point['description']})
    - My Product/Service: {product_name} - {product_description}
    
    Task:
    Write a 3-email cold outreach sequence:
    1. "intro": Empathize with the pain point, briefly mention a better way. Value-first.
    2. "value": Explain HOW the product solves the pain point. Include a placeholder for a case study.
    3. "close": A direct call to action (demo/call).
    
    Tone: Professional, concise, not salesy. "Helpful expert" vibe.
    
    Return a JSON array of objects with keys: "stage", "subject", "body".
    "body" should be HTML-ready (use <br> for breaks), but Keep it simple.
    Use placeholders like {{Contact Person}} and {{Business Name}}.
    """

    print(f"Generating copy for pain point: {pain_point['title']}...")

    provider = LLMFactory.get_provider()
    result = provider.generate_json(prompt)
    
    if isinstance(result, list):
        return result
    
    print("Copywriter failed to get valid JSON results.")
    return []

if __name__ == "__main__":
    # Test
    from dotenv import load_dotenv
    load_dotenv()
    sample_pain = {"title": "Slow Design Renders", "description": "Designers wait hours for renders, killing productivity."}
    emails = generate_campaign_sequence("Interior Design", sample_pain, "RenderFast Cloud", "Cloud-based GPU rendering farm")
    print(json.dumps(emails, indent=2))
