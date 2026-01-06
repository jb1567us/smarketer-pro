def get_agent_class(agent_name):
    """
    Returns the agent class for a given name (case-insensitive).
    """
    # Lazy imports to avoid circular dependencies
    from agents import (
        ResearcherAgent, QualifierAgent, CopywriterAgent, ReviewerAgent, 
        GraphicsDesignerAgent, WordPressAgent, SocialMediaAgent, AdCopyAgent,
        BrainstormerAgent, PersonaAgent, ManagerAgent, ProductManagerAgent,
        SyntaxAgent, UXAgent, SEOExpertAgent, InfluencerAgent, SocialListeningAgent, LinkedInAgent
    )
    
    agent_map = {
        "researcher": ResearcherAgent,
        "qualifier": QualifierAgent,
        "copywriter": CopywriterAgent,
        "reviewer": ReviewerAgent,
        "designer": GraphicsDesignerAgent,
        "wordpress": WordPressAgent,
        "social_media": SocialMediaAgent,
        "ad_copy": AdCopyAgent,
        "brainstormer": BrainstormerAgent,
        "persona": PersonaAgent,
        "product_manager": ProductManagerAgent,
        "seo": SEOExpertAgent,
        "influencer": InfluencerAgent,
        "social_listener": SocialListeningAgent,
        "linkedin": LinkedInAgent
    }
    
    return agent_map.get(agent_name.lower())

def list_available_agents():
    """
    Returns a list of available agent keys.
    """
    # Hardcoded keys to avoid importing agents module at import time
    return [
        "researcher", "qualifier", "copywriter", "reviewer", "designer", 
        "wordpress", "social_media", "ad_copy", "brainstormer", 
        "persona", "product_manager", "seo", "influencer", 
        "social_listener", "linkedin"
    ]
