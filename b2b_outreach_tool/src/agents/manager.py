from .base import BaseAgent
from .researcher import ResearcherAgent
from .qualifier import QualifierAgent
from .copywriter import CopywriterAgent
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

    async def run_mission(self, goal, context=None):
        """
        Takes a high-level goal (e.g. "Find 5 leads for my Design Agency in Austin") 
        and executes the full pipeline.
        """
        # 1. Plan
        # Ask Manager logic (LLM) how to approach this.
        # For now, we will use a semi-structured 'Thought' process.
        
        plan_prompt = (
            f"Goal: {goal}\n"
            f"Context: {context}\n"
            "You have access to: Researcher, Qualifier, Copywriter.\n"
            "Break this down into steps. For this MVP, we assume a standard flow: Research -> Qualify -> Write.\n"
            "Identify the 'Search Queries' needed for the Researcher."
            "Extract the number of leads requested if specified (default to 5 if not clear)."
            "Return JSON: {'search_queries': [str], 'icp_criteria': str, 'value_proposition': str, 'limit': int}"
        )
        
        plan = self.provider.generate_json(plan_prompt)
        
        if not plan:
            return {"error": "Failed to generate plan."}
            
        limit = plan.get('limit', 5)
        
        report = {
            "plan": plan,
            "leads": []
        }
        
        # 2. Execute Research
        for query in plan.get('search_queries', [])[:1]: # Limit to 1 query for safety/cost
            search_res = await self.researcher.gather_intel({"query": query, "limit": limit})
            
            # 3. Process Leads
            if 'results' in search_res:
                for url_info in search_res['results'][:limit]: 
                    url = url_info['url']
                    lead_intel = await self.researcher.gather_intel({"url": url})
                    
                    if not lead_intel.get('html_preview'): continue
                    
                    # 4. Qualify
                    q_ctx = f"URL: {url}\nPreview: {lead_intel['html_preview']}\nCriteria: {plan.get('icp_criteria')}"
                    q_res = self.qualifier.think(q_ctx)
                    
                    if q_res and q_res.get('qualified'):
                        # 5. Write
                        c_ctx = f"Lead: {lead_intel}\nValue Prop: {plan.get('value_proposition')}"
                        draft = self.copywriter.think(c_ctx)
                        
                        report['leads'].append({
                            "url": url,
                            "qualification": q_res,
                            "draft": draft
                        })
                        
        return report

    def think(self, context):
        return "I am an async agent. Use 'run_mission' to execute complex workflows."
