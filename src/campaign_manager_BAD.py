import sys
import os
import argparse
import time
import asyncio

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_connection, save_pain_points, get_pain_points, save_template, get_templates, get_leads_by_status, mark_contacted
from mailer import Mailer
from config import config
from agents import ResearcherAgent, CopywriterAgent, ReviewerAgent, SyntaxAgent

from src.policy import PolicyProfile
from src.engine.strategy_factory import StrategyFactory

# UI Wrappers
def start_campaign_step_research(niche, product_context=None):
    pain_points = get_pain_points(niche)
    
    if not pain_points or product_context: 
        # === AGENT INTEGRATION ===
        print("  [Agent] Researcher is analyzing niche...")
        agent = ResearcherAgent()
        
        async def run_research():
            return await agent.gather_intel({"query": f"common business pain points for {niche} companies"})
        
        prompt = f"Identify 5 critical business pain points for companies in the '{niche}' industry. Return JSON list with 'title' and 'description'."
        if product_context:
            prompt += f"\nContext: My product does this: {product_context}\nFocus on pain points my product solves."
            
        result = agent.provider.generate_json(prompt)
        
        if result and isinstance(result, list):
             save_pain_points(niche, result)
             pain_points = get_pain_points(niche) # Re-fetch
    return pain_points

def refine_campaign_step_research(niche, kept_points, feedback, product_context=None):
    agent = ResearcherAgent()
    prompt = f"The user kept these pain points for {niche}: {kept_points}\nFeedback: {feedback}\nProduct Context: {product_context}\nGenerate 3 NEW, better pain points. JSON list."
    result = agent.provider.generate_json(prompt)
    if result and isinstance(result, list):
        save_pain_points(niche, result)
    return get_pain_points(niche)

def start_campaign_step_copy(niche, pain_point, product_name, product_description, campaign_id=None, policy: PolicyProfile = None):
    # === STRATEGY DELEGATION ===
    print("  [CampaignManager] Delegating copy generation to Strategy...")
    
    if not policy:
        policy = PolicyProfile.default_white_hat(tool_name="copywriter")
    
    strategy = StrategyFactory.get_outreach_strategy(policy)
    
    context = {
        "niche": niche,
        "pain_point": pain_point.get('title') + " - " + pain_point.get('description') if isinstance(pain_point, dict) else str(pain_point),
        "product_name": product_name,
        "product_description": product_description
    }
    
    # Generate content via strategy (Polymorphic)
    # White Hat -> Agents
    # Black Hat -> Spintax
    draft = strategy.generate_message_body(context)
    
    # Return as list of 1 for now (to match existing sequence structure)
    sequence = [{
        "stage": "intro",
        "subject": draft.get('subject_line'),
        "body": draft.get('body')
    }]
    
    # Save to DB if campaign_id is present
    if campaign_id:
        save_template(
            niche=niche,
            pain_point_id=pain_point['id'],
            stage="intro",
            subject=draft.get('subject_line'),
            body=draft.get('body'),
            campaign_id=campaign_id
        )
        
    return sequence

def start_campaign_step_send(leads, confirmation=False):
    pass

def run_campaign(niche, product_name, product_description, send=False, auto=False):
    pass 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("niche", help="Target Industry/Niche")
    parser.add_argument("product", help="Your Product Name")
    parser.add_argument("desc", help="Product Description")
    args = parser.parse_args()
    
    # Just testing the research step
    print(start_campaign_step_research(args.niche, args.desc))
