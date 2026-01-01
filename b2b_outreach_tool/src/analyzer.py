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

def analyze_lead_qualification(url, content, icp_criteria):
    """
    Analyzes if a lead meets the Ideal Customer Profile (ICP) criteria.
    Returns (score, reason) where score is 0-100.
    """
    if not content or not icp_criteria:
        return 0, "No content or criteria provided"

    # Truncate content
    truncated_content = content[:15000]

    prompt = f"""
    Act as a Lead Qualification Specialist.
    Review the website content for {url} against the following Ideal Customer Profile (ICP).

    ICP Criteria:
    {icp_criteria}

    Content:
    {truncated_content}

    Task:
    1. Score the lead from 0 to 100 based on how well it fits the ICP.
       - 100: Perfect match (meets all 'must haves', no 'deal breakers').
       - 0: Complete mismatch (violates 'must haves' or has 'deal breakers').
    2. Provide a concise reason for the score (1 sentence).

    Return JSON:
    {{
        "score": integer,
        "reason": "string"
    }}
    """

    try:
        provider = LLMFactory.get_provider()
        result = provider.generate_json(prompt)
        
        if result:
            return result.get("score", 0), result.get("reason", "Analysis failed")
    except Exception as e:
        print(f"Qualification error: {e}")
        return 0, f"Error: {e}"

    return 0, "Unknown error"
