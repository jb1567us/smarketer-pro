from .base import BaseAgent
from .researcher import ResearcherAgent
from .qualifier import QualifierAgent
from .copywriter import CopywriterAgent
from .linkedin import LinkedInAgent
import json
import asyncio

class ManagerAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Outreach Campaign Manager",
            goal="Orchestrate the entire outreach process by delegating tasks to specialized agents (Researcher, Qualifier, Copywriter).",
            provider=provider
        )
        self.researcher = ResearcherAgent(provider)
        self.qualifier = QualifierAgent(provider)
        self.copywriter = CopywriterAgent(provider)
        self.linkedin = LinkedInAgent(provider)

    async def run_mission(self, goal, context=None):
        """
        Takes a high-level goal and executes the full multichannel pipeline.
        """
        # 1. Plan
        plan_prompt = (
            f"Goal: {goal}\n"
            f"Context: {context}\n"
            "You have access to: Researcher, Qualifier, Copywriter, LinkedIn Specialist.\n"
            "Standard multi-touch flow: Research -> Qualify -> Multi-touch Plan (Email + LinkedIn) -> Execution.\n"
            "Identify search queries and ICP criteria.\n"
            "Return JSON: {\n"
            "  'search_queries': [str],\n"
            "  'icp_criteria': str,\n"
            "  'value_proposition': str,\n"
            "  'channels': ['email', 'linkedin'],\n"
            "  'limit': int\n"
            "}"
        )
        
        plan = self.provider.generate_json(plan_prompt)
        if not plan: return {"error": "Plan generation failed"}
        
        limit = plan.get('limit', 5)
        report = {"plan": plan, "leads": []}
        
        # 2. Execution Loop
        for query in plan.get('search_queries', [])[:1]:
            search_res = await self.researcher.gather_intel({"query": query, "limit": limit})
            if 'results' not in search_res: continue
            
            for url_info in search_res['results'][:limit]:
                url = url_info['url']
                # Research & Enrich
                lead_intel = await self.researcher.gather_intel({"url": url})
                if not lead_intel.get('html_preview'): continue
                
                # Qualify
                q_res = self.qualifier.think(f"URL: {url}\nIntel: {lead_intel}\nCriteria: {plan['icp_criteria']}")
                if not q_res or not q_res.get('qualified'): continue
                
                # Multichannel Drafting
                res = {"url": url, "qualification": q_res, "drafts": {}}
                
                if 'email' in plan.get('channels', []):
                    res['drafts']['email'] = self.copywriter.think(f"Lead: {lead_intel}\nValue Prop: {plan['value_proposition']}")
                
                if 'linkedin' in plan.get('channels', []):
                    res['drafts']['linkedin'] = self.linkedin.think(f"Lead: {lead_intel}\nValue Prop: {plan['value_proposition']}")
                
                report['leads'].append(res)
                
        # Remember the mission context for future tuning
        self.remember(f"mission_{hash(goal)}", {"goal": goal, "plan": plan, "result_count": len(report['leads'])})
        
        return report

    def think(self, context):
        return "I am an async agent. Use 'run_mission' to execute complex workflows."
