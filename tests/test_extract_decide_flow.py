import sys
import os
import asyncio
import json
from unittest.mock import MagicMock

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from agents.researcher import ResearcherAgent
from agents.qualifier import QualifierAgent
from agents.copywriter import CopywriterAgent
from llm.base import LLMProvider

class MockLLMProvider(LLMProvider):
    def __init__(self):
        self.last_prompt = None

    def generate_text(self, prompt, **kwargs):
        self.last_prompt = prompt
        return "Mocked Text Output"

    def generate_json(self, prompt, **kwargs):
        self.last_prompt = prompt
        
        # Simple routing based on prompt content
        if "search-engine queries for B2B lead discovery" in prompt or "discovery_query_generator" in prompt:
            return {
                "version": "1.0",
                "query_groups": [
                    {
                        "group": "broad_discovery",
                        "queries": [
                            {"q": 'site:linkedin.com "VP of Sales" SaaS', "intent": "Find B2B sales leads", "expected_results": "LinkedIn profiles", "priority": 1}
                        ]
                    }
                ]
            }
        
        if "PAGE_TARGETING_PLANNER" in prompt or "Recommends which URLs to fetch next" in prompt or "URLs to fetch next from the same domain" in prompt:
            return {
                "version": "1.0",
                "targets": [
                    {"suggested_url": "https://example.com/about", "reason": "Determine industry and team size", "priority": 1, "what_to_extract": ["team_size", "industry"]}
                ]
            }

        if "LEAD_SIGNAL_EXTRACTOR" in prompt or "extract structured signals from provided page text" in prompt.lower() or "extract_lead_signals" in prompt or "Evidence or Unknown" in prompt:
            return {
                "version": "1.0",
                "candidate": {"domain": "example.com", "seed_url": "https://example.com/"},
                "evidence": [
                    {"id": 1, "url": "https://example.com/about", "quote": "We are a leading SaaS provider for sales teams."}
                ],
                "signals": {
                    "industry": {"value": "SaaS", "confidence": "high", "evidence_ids": [1]},
                    "offerings": [{"value": "Sales CRM", "evidence_ids": [1]}],
                    "audience": {"served_markets": "B2B", "b2b_vs_b2c": "b2b", "evidence_ids": [1]},
                    "geo": {"locations_found": ["USA"], "primary_geo": "USA", "evidence_ids": [1]},
                    "size_signals": {"locations_count_claimed": "1", "team_size_hint": "50-100", "evidence_ids": [1]},
                    "contact": {"emails": ["sales@example.com"], "phones": [], "contact_urls": ["/contact"], "evidence_ids": [2]},
                    "keywords": ["SaaS", "Sales"],
                    "red_flags": []
                },
                "missing_info": []
            }

        if "ICP_QUALIFICATION_DECIDER" in prompt or "ICP qualification engine" in prompt or "icp_qualification_decider" in prompt:
            return {
                "version": "1.0",
                "qualified": True,
                "score": 900,
                "confidence": "high",
                "gates": {
                    "must_have_passed": True,
                    "must_not_triggered": True,
                    "details": [
                        {"gate": "SaaS Industry", "status": "pass", "why": "Company explicitly states they are SaaS", "evidence_ids": [1]}
                    ]
                },
                "score_breakdown": [
                    {"factor": "Industry Match", "points_awarded": 200, "max_points": 200, "why": "Perfect industry match", "evidence_ids": [1]}
                ],
                "reason": "Highly qualified SaaS B2B company.",
                "missing_info": [],
                "followup_actions": [{"action": "Reach out to VP of Sales", "priority": 1}]
            }

        if "GROUNDED_OUTREACH_WRITER" in prompt or "outreach messages that are grounded in provided evidence" in prompt.lower() or "grounded_outreach_writer" in prompt:
            return {
                "version": "1.0",
                "personalization_anchors": [
                    {"observed_detail": "Mentioned being a leading SaaS provider for sales teams.", "why_relevant": "Fits our sales automation value prop.", "evidence_ids": [1]}
                ],
                "messages": [
                    {
                        "channel": "email",
                        "tone": "direct",
                        "subject": "Question about example.com's sales automation",
                        "body": "Hi, I noticed you mention being a leading SaaS provider for sales teams. We help SaaS companies like yours...",
                        "cta": "Quick call next week?",
                        "evidence_ids_used": [1]
                    }
                ],
                "missing_info": []
            }

        return {}

async def test_flow():
    mock_provider = MockLLMProvider()
    
    researcher = ResearcherAgent(provider=mock_provider)
    qualifier = QualifierAgent(provider=mock_provider)
    copywriter = CopywriterAgent(provider=mock_provider)
    
    # Load example ICP/Offering
    with open("c:/sandbox/b2b_outreach_tool/examples/example_icp_offering.json", "r") as f:
        data = json.load(f)
    
    icp = data['icp']
    offering = data['offering']
    constraints = data['constraints']
    
    print("\n--- 1. Discovery Query Generation ---")
    queries = researcher.generate_discovery_queries(icp, offering, constraints)
    print(f"Generated {sum(len(g['queries']) for g in queries.get('query_groups', []))} queries in {len(queries.get('query_groups', []))} groups.")
    assert "query_groups" in queries
    
    print("\n--- 2. Page Targeting Plan ---")
    candidate = {"domain": "example.com", "seed_url": "https://example.com/"}
    pages_seen = [{"url": "https://example.com/", "title": "Home"}]
    plan = researcher.plan_page_targeting(icp, candidate, pages_seen)
    print(f"Recommended {len(plan.get('targets', []))} next pages.")
    assert "targets" in plan

    print("\n--- 3. Lead Signal Extraction ---")
    pages = [{"url": "https://example.com/", "text": "We are a leading SaaS provider for sales teams. Contact us at sales@example.com"}]
    signals = await researcher.extract_lead_signals(icp, candidate, pages)
    print(f"Extracted signals for: {signals.get('signals', {}).get('industry', {}).get('value', 'Unknown')}")
    assert "signals" in signals

    print("\n--- 4. ICP Qualification Decision ---")
    decision = qualifier.decide_qualification(icp, signals)
    print(f"Qualified: {decision.get('qualified')}, Score: {decision.get('score')}")
    assert "qualified" in decision

    print("\n--- 5. Grounded Outreach Writing ---")
    outreach = copywriter.write_grounded_outreach(icp, offering, candidate, signals, decision)
    print(f"Generated {len(outreach.get('messages', []))} outreach messages.")
    assert "messages" in outreach
    print(f"First message subject: {outreach['messages'][0]['subject']}")

    print("\n✅ END-TO-END FLOW VERIFIED (MOCKED PROVIDER)")

if __name__ == "__main__":
    asyncio.run(test_flow())
