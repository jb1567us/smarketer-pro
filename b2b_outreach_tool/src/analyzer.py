import os
import json
import time
from llm import LLMFactory

def analyze_content(url, content, target_niche=None):
    """
    Analyzes website content using the configured LLM Provider.
    """
    if not content:
        return None

    # Truncate content to avoid token limits (approx 10k chars)
    truncated_content = content[:15000]

    prompt = f"""
    Act as a Business Analyst. 
    Analyze the following website content from {url}.
    
    Target Niche Context: {target_niche if target_niche else "General B2B"}
    
    Extract/Determine:
    1. Business Name
    2. Industry (Be specific)
    3. Business Type (B2B, B2C, Agency, SaaS, etc.)
    4. Summary (1 sentence)
    5. Confidence Score (0.0 to 1.0) that this is a legitimate operating business.
    6. Is Relevant: True/False (Is this business relevant to the Target Niche? If niche is None, assume True).
    7. Relevance Reason: Why is it relevant or not?
    8. Address: Physical address if found, else "Unknown".
    9. Phone Number: Phone if found, else "Unknown".
    10. Contact Person: Name of specific person (Founder, CEO, Principal, etc.) if found, else "Unknown".

    Content:
    {truncated_content}

    Return a JSON object with keys: 
    "business_name", "industry", "business_type", "summary", "confidence", "is_relevant", "relevance_reason", "address", "phone_number", "contact_person".
    """

    provider = LLMFactory.get_provider()
    analysis = provider.generate_json(prompt)
    
    if analysis:
        # Normalize keys if needed (LLM usually handles this well given the prompt)
        return analysis

    return {
        "business_name": "Unknown",
        "industry": "Unknown",
        "business_type": "Unknown",
        "summary": "Analysis failed",
        "address": "Unknown",
        "phone_number": "Unknown",
        "contact_person": "Unknown",
        "confidence": 0.0,
        "is_relevant": False,
        "relevance_reason": "LLM Error"
    }
