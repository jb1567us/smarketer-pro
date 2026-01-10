import concurrent.futures
import os
import json
from llm import LLMFactory

def _get_available_research_providers():
    """Returns a list of provider names that have API keys configured."""
    providers = []
    # Core providers that differ significantly in reasoning
    if os.getenv("GEMINI_API_KEY"):
        providers.append("gemini")
    if os.getenv("GROQ_API_KEY"):
         # specific fast model for groq
        providers.append("groq") 
    if os.getenv("MISTRAL_API_KEY"):
        providers.append("mistral")
    if os.getenv("OPENROUTER_API_KEY"):
        providers.append("openrouter")
        
    return providers

def _research_single(provider_name, prompt):
    """Executes the prompt with a specific provider."""
    try:
        # Access internal factory method to instantiate ad-hoc
        # Note: This relies on the static method in LLMFactory
        provider = LLMFactory._create_provider(provider_name)
        print(f"  -> Asking {provider_name}...")
        result = provider.generate_json(prompt)
        
        if result:
             if isinstance(result, dict) and 'pain_points' in result:
                return result['pain_points']
             elif isinstance(result, list):
                return result
    except Exception as e:
        print(f"  -> {provider_name} failed: {e}")
    return []

def research_niche(niche, product_context=None):
    """
    Analyzes a niche using an ENSEMBLE of LLMs to identify top pain points.
    Returns a unified list of dicts.
    """
    
    # 1. Define the Research Prompt
    prompt = f"""
    Act as a B2B Market Researcher.
    Analyze the "{niche}" industry.
    """
    
    if product_context:
        prompt += f"""
        I am marketing a product/service described as: "{product_context}".
        Identify the TOP 5 most critical pain points in this niche THAT MY PRODUCT SOLVES.
        Focus strictly on problems relevant to my offering.
        """
    else:
        prompt += f"""
        Identify the TOP 5 most critical pain points, challenges, or "bleeding neck" problems faced by businesses in this niche right now.
        """
        
    prompt += """
    Return a list of JSON objects. Each object must have:
    - "title": A short, punchy title for the pain point (3-7 words).
    - "description": A 2-sentence explanation of why this is a problem and its business impact.
    """

    # 2. Identify Experts
    providers = _get_available_research_providers()
    
    if not providers:
        print("No LLM keys found. checking default...")
        providers = ['gemini'] # Fallback
    
    # Limit to 3 diverse experts to save time/tokens if many keys exist
    # prioritize distinct model families if possible, but simple slicing is fine for now
    selected_providers = providers[:3] 
    
    print(f"Researching pain points for: '{niche}' using Ensemble: {selected_providers}...")

    # 3. Parallel Execution
    all_pain_points = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_provider = {executor.submit(_research_single, p, prompt): p for p in selected_providers}
        for future in concurrent.futures.as_completed(future_to_provider):
            points = future.result()
            if points:
                all_pain_points.extend(points)
    
    if not all_pain_points:
        print("Ensemble research failed. Returning empty.")
        return []

    # 4. Aggregation & Synthesis
    print(f"Aggregating {len(all_pain_points)} raw insights into Top 5...")
    
    synthesis_prompt = f"""
    I have conducted research on the "{niche}" industry using multiple AI analysts.
    Here is the combined list of raw pain points identified:
    
    {json.dumps(all_pain_points, indent=2)}
    
    Your task:
    1. Deduplicate similar points.
    2. Merge overlapping insights.
    3. Select the ABSOLUTE TOP 5 most critical/valuable pain points from this list.
    4. Rewrite them to be compelling and business-focused.
    
    Return the final Top 5 as a JSON list of objects with "title" and "description".
    """
    
    # Use the default/main provider for the final synthesis (usually the smart router or best model)
    synthesizer = LLMFactory.get_provider()
    final_result = synthesizer.generate_json(synthesis_prompt)
    
    if final_result:
        if isinstance(final_result, dict) and 'pain_points' in final_result:
            return final_result['pain_points']
        elif isinstance(final_result, list):
            return final_result

    print("Synthesis failed. Returning raw list (truncated).")
    return all_pain_points[:5]

def refine_pain_points(niche, kept_points, feedback, product_context=None):
    """
    Generates NEW pain points based on feedback, while preserving kept_points.
    """
    prompt = f"""
    Act as a B2B Market Researcher.
    
    Context:
    - Niche: {niche}
    - Product Context: {product_context if product_context else "None provided"}
    
    Current Status:
    The user has selected the following pain points to KEEP:
    {json.dumps(kept_points, indent=2)}
    
    User Feedback for Tuning:
    "{feedback}"
    
    Task:
    Generate 3-5 NEW, DISTINCT pain points that:
    1. Align with the user's feedback.
    2. Complement the 'Kept' points (do NOT duplicate them).
    3. Are deep, specific, and valuable.
    
    Return a list of JSON objects (title, description). 
    """
    
    print(f"Refining pain points for: {niche}...")

    provider = LLMFactory.get_provider()
    new_points = provider.generate_json(prompt)
    
    if new_points:
         if isinstance(new_points, dict) and 'pain_points' in new_points:
             new_points = new_points['pain_points']
    
    if not isinstance(new_points, list):
        new_points = []
        
    # Combine
    final_list = kept_points + new_points
    return final_list

if __name__ == "__main__":
    # Test
    from dotenv import load_dotenv
    load_dotenv()
    points = research_niche("Interior Design Firms")
    print(json.dumps(points, indent=2))
