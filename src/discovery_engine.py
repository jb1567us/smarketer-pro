import random
from agents import ResearcherAgent

class DiscoveryEngine:
    def __init__(self):
        self.researcher = ResearcherAgent()
        self.topics = [
            "Emerging trends in B2B marketing",
            "New AI tools for sales automation",
            "Unconventional lead generation strategies",
            "Psychology of cold outreach",
            "Data enrichment best practices",
            "Growth hacking case studies"
        ]

    async def plan_structured_discovery(self, icp, offering, constraints=None):
        """
        Generates high-precision queries for a target ICP and offering.
        """
        return self.researcher.generate_discovery_queries(icp, offering, constraints or {})

    async def get_serendipitous_finding(self, current_niche=None):
        """
        Returns a 'Did you know?' or 'Opportunity Alert' item.
        Uses the ResearcherAgent to find something fresh.
        """
        # Pick a topic that is arguably relevant but potentially outside strict echo chamber
        base_topic = random.choice(self.topics)
        
        query = f"latest interesting fact or trend about {base_topic}"
        if current_niche:
             if random.random() > 0.5:
                 query = f"cross-industry innovation joining {current_niche} and {base_topic}"
        
        # Simple synchronous wrapper for now, assuming called from sync context or we await it
        # Actually ManagerAgent is usually sync, but UI is async capable. 
        # For simplicity in this v1, we'll assume the manager calls this via a helper or direct await if async.
        # But wait, ResearcherAgent.gather_intel IS async. 
        # We will expose an async method here.
        
        try:
            intel = await self.researcher.gather_intel({"query": query, "limit": 1})
            results = intel.get("results", [])
            
            if results:
                top_result = results[0]
                if isinstance(top_result, dict):
                     return {
                         "type": "discovery",
                         "title": f"Industry Insight: {base_topic}",
                         "content": top_result.get("title", "Check this out"),
                         "url": top_result.get("url"),
                         "snippet": top_result.get("snippet", "")[:200] + "..."
                     }
            
            return None
        except Exception as e:
            print(f"Discovery Engine Error: {e}")
            return None
