AGENT_METADATA = {
    "researcher": {
        "role": "Lead Researcher & Harvester",
        "expertise": "Web scraping, lead discovery, footprint analysis, mass harvesting.",
        "capabilities": ["mass_harvest", "gather_intel", "check_technographics"],
        "best_used_for": "Finding raw leads, identifying tech stacks, and gathering domain intelligence."
    },
    "qualifier": {
        "role": "Lead Qualification Specialist",
        "expertise": "Lead scoring, relevance analysis, pain point identification.",
        "capabilities": ["qualify_lead", "analyze_relevance"],
        "best_used_for": "Filtering raw leads based on ICP and finding emotional hooks."
    },
    "copywriter": {
        "role": "Conversion Copywriter",
        "expertise": "Email outreach, ad copy, spintax, personalization.",
        "capabilities": ["generate_email", "write_ad_copy", "generate_spintax", "optimize_campaign"],
        "best_used_for": "Crafting high-converting outreach messages and marketing copy."
    },
    "reviewer": {
        "role": "Quality Control / Editor",
        "expertise": "Proofreading, brand alignment, tone consistency, and conversion optimization.",
        "capabilities": ["review_content", "enhance_email_conversion", "audit_tone"],
        "best_used_for": "Final audit of copy and maximizing email reply rates."
    },
    "designer": {
        "role": "Visual Brand Designer",
        "expertise": "UI/UX layout, brand assets, social graphics.",
        "capabilities": ["design_layout", "create_asset_specs"],
        "best_used_for": "Planning visual elements and brand aesthetics."
    },
    "seo": {
        "role": "SEO Architect & Link Builder",
        "expertise": "Backlink strategy, keyword research, link wheels, CTR boosting.",
        "capabilities": ["perform_audit", "research_keywords", "build_link_wheel", "simulate_ctr"],
        "best_used_for": "Boosting organic rankings and site authority."
    },
    "video": {
        "role": "AI Video Producer",
        "expertise": "Short-form video, AI voiceovers, visual storytelling.",
        "capabilities": ["generate_video_script", "coordinate_video_gen"],
        "best_used_for": "Creating viral-ready video content for social platforms."
    },
    "image": {
        "role": "AI Image Artist",
        "expertise": "Prompt engineering, visual assets, consistent branding.",
        "capabilities": ["generate_image", "edit_image"],
        "best_used_for": "Generating high-quality custom visuals for campaigns."
    },
    "product_manager": {
        "role": "Technical Product Manager",
        "expertise": "System architecture, requirement specs, data modeling.",
        "capabilities": ["think", "generate_campaign_strategy"],
        "best_used_for": "High-level planning, defining logic, and architecting new features."
    },
    "manager": {
        "role": "System Conductor & Manager",
        "expertise": "Orchestration, delegation, workflow automation.",
        "capabilities": ["think", "run_mission", "conductor_mission"],
        "best_used_for": "Total system control, multi-agent coordination, and goal achievement."
    },
    "wordpress": {
        "role": "Webmaster / CMS Expert",
        "expertise": "WordPress management, content publishing, plugin config.",
        "capabilities": ["publish_post", "manage_site"],
        "best_used_for": "Automating site updates and multi-site management."
    },
    "influencer": {
        "role": "Influencer Scout",
        "expertise": "Finding high-impact creators and influencers in specific niches.",
        "capabilities": ["scout_influencers", "analyze_profile"],
        "best_used_for": "Identifying social media influencers for outreach campaigns."
    },
    "social_media": {
        "role": "Expert Social Media Strategist",
        "expertise": "Generate high-engagement social media posts for various platforms, including TikTok and Instagram.",
        "capabilities": ["generate_tiktok_strategy", "generate_instagram_strategy", "think"],
        "best_used_for": "Creating viral content strategies and platform-specific posts."
    },
    "ad_copy": {
        "role": "Direct Response Copywriter",
        "expertise": "Write high-converting ad copy for Google, Facebook, and LinkedIn.",
        "capabilities": ["think"],
        "best_used_for": "Paid advertising campaigns and landing page copy."
    },
    "brainstormer": {
        "role": "Creative Campaign Director",
        "expertise": "Brainstorm innovative campaign angles, hooks, and themes.",
        "capabilities": ["think"],
        "best_used_for": "Generating new marketing ideas and unique angles."
    },
    "persona": {
        "role": "Market Research Analyst",
        "expertise": "Create detailed Ideal Customer Personas (ICPs) based on market data.",
        "capabilities": ["think"],
        "best_used_for": "Defining target audiences and understanding customer psychology."
    },
    "social_listener": {
        "role": "Social Media Guardian",
        "expertise": "Monitoring social platforms for brand mentions, competitor weakness, and high-intent buying signals. Trend analysis.",
        "capabilities": ["listen_for_keywords", "analyze_signal", "generate_reply", "analyze_platform_trends", "generate_trend_report"],
        "best_used_for": "Real-time monitoring, lead detection, and viral hook generation."
    },
    "linkedin": {
        "role": "LinkedIn Outreach Specialist",
        "expertise": "Draft high-converting LinkedIn InMail and connection requests based on profile highlights and intent signals.",
        "capabilities": ["think", "generate_comment"],
        "best_used_for": "Professional networking and B2B outreach on LinkedIn."
    },
    "contact_form": {
        "role": "Contact Form Specialist",
        "expertise": "Identify and submit personalized messages through website contact forms.",
        "capabilities": ["submit_contact_form"],
        "best_used_for": "Bypassing email filters by sending messages directly via website forms."
    },
    "ux": {
        "role": "User Interface & Experience Designer",
        "expertise": "Decide the best way to visualize data in a Streamlit application.",
        "capabilities": ["think"],
        "best_used_for": "Designing intuitive data dashboards and user interfaces."
    },
    "syntax": {
        "role": "Syntax & Structural Integrity Specialist",
        "expertise": "Ensure content is technically correct, free of placeholders, and properly formatted.",
        "capabilities": ["think"],
        "best_used_for": "Final code/text validation and error checking."
    },
    "data_cleaner": {
        "role": "DataOps Pythonista",
        "expertise": "Cleaning and standardizing messy B2B lead lists (CSV/Excel).",
        "capabilities": ["think"],
        "best_used_for": "Preprocessing leads before import."
    },
    "sales_analyzer": {
        "role": "Meeting Minute Writer",
        "expertise": "Analyzing sales calls and generating actionable minutes.",
        "capabilities": ["think"],
        "best_used_for": "Post-call analysis and action item extraction."
    },
    "knowledge_architect": {
        "role": "Knowledge Architect",
        "expertise": "Structuring unstructured data for RAG/Database ingestion.",
        "capabilities": ["think"],
        "best_used_for": "Building the Knowledge Graph."
    },
    "prompt_expert": {
        "role": "Prompt Engineer",
        "expertise": "Optimizing and refining prompts for other agents.",
        "capabilities": ["think"],
        "best_used_for": "Meta-optimization of system prompts."
    },
    "summarizer": {
        "role": "Content Synthesizer",
        "expertise": "Condensing large documents and articles into concise summaries.",
        "capabilities": ["summarize_text", "extract_key_points"],
        "best_used_for": "Digestible summaries of large datasets or documents."
    },
    "meet_scribe": {
        "role": "Meeting Intelligence Officer",
        "expertise": "Analyzing meeting transcripts, extracting action items, drafting minutes and follow-ups.",
        "capabilities": ["analyze_meeting_transcript", "generate_follow_up_email"],
        "best_used_for": "Post-meeting automation and ensuring accountability."
    }
}

def get_agent_metadata(agent_name):
    """
    Returns metadata for a given agent name.
    Supports both static system agents and dynamic custom agents.
    """
    # 1. Check static metadata
    if agent_name.lower() in AGENT_METADATA:
        return AGENT_METADATA[agent_name.lower()]
    
    # 2. Check custom agents via database
    try:
        from database import get_custom_agents
        custom_agents = get_custom_agents()
        for ca in custom_agents:
            if ca['name'].lower() == agent_name.lower():
                return {
                    "role": ca['role'],
                    "expertise": ca['goal'], # Goal serves as expertise summary for custom agents
                    "capabilities": ["think"], # Default capability for custom agents
                    "best_used_for": f"Custom task: {ca['goal']}"
                }
    except Exception as e:
        print(f"Error fetching custom agent metadata for {agent_name}: {e}")
        
    return {}

def get_agent_class(agent_name):
    """
    Returns the agent class for a given name (case-insensitive).
    For Custom Agents, returns a factory function that instantiates CustomAgent with stored config.
    """
    # Lazy imports to avoid circular dependencies
    from agents import (
        ResearcherAgent, QualifierAgent, CopywriterAgent, ReviewerAgent, 
        GraphicsDesignerAgent, WordPressAgent, SocialMediaAgent, AdCopyAgent,
        BrainstormerAgent, PersonaAgent, ManagerAgent, ProductManagerAgent,
        SyntaxAgent, UXAgent, SEOExpertAgent, InfluencerAgent, SocialListeningAgent, 
        LinkedInAgent, ContactFormAgent, VideoAgent, ImageGenAgent,
        DataCleanerAgent, SalesAnalyzerAgent, KnowledgeArchitectAgent, PromptExpertAgent,
        SummarizerAgent, MeetScribeAgent
    )
    from agents.custom_agent import CustomAgent
    
    name_lower = agent_name.lower()
    
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
        "linkedin": LinkedInAgent,
        "contact_form": ContactFormAgent,
        "video": VideoAgent,
        "image": ImageGenAgent,
        "manager": ManagerAgent,
        "ux": UXAgent,
        "syntax": SyntaxAgent,
        "data_cleaner": DataCleanerAgent,
        "sales_analyzer": SalesAnalyzerAgent,
        "knowledge_architect": KnowledgeArchitectAgent,
        "prompt_expert": PromptExpertAgent,
        "summarizer": SummarizerAgent,
        "meet_scribe": MeetScribeAgent
    }
    
    # 1. Check standard agents
    if name_lower in agent_map:
        return agent_map[name_lower]
        
    # 2. Check custom agents
    try:
        from database import get_custom_agents
        custom_agents = get_custom_agents()
        for ca in custom_agents:
            if ca['name'].lower() == name_lower:
                # Capture values in closure for the factory
                def custom_agent_factory(provider=None):
                    return CustomAgent(
                        name=ca['name'],
                        role=ca['role'],
                        goal=ca['goal'],
                        system_prompt=ca['system_prompt'],
                        provider=provider
                    )
                return custom_agent_factory
    except Exception as e:
        print(f"Error fetching custom agent class for {agent_name}: {e}")
    
    return None

def list_available_agents():
    """
    Returns a list of available agent keys (system + custom).
    """
    keys = list(AGENT_METADATA.keys())
    
    try:
        from database import get_custom_agents
        custom_agents = get_custom_agents()
        keys.extend([ca['name'].lower() for ca in custom_agents])
    except Exception as e:
        print(f"Error listing custom agents: {e}")
        
    return list(set(keys)) # unique list
