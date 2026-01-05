import json
import asyncio
from database import update_lead_enrichment, get_lead_by_id
from agents import ResearcherAgent
from config import config


class EnrichmentManager:
    def __init__(self):
        self.researcher = ResearcherAgent()

    async def enrich_lead(self, lead_id):
        """
        Orchestrates the researcher to find social and intent data for a lead.
        """
        lead = get_lead_by_id(lead_id)
        if not lead:
            return {"error": "Lead not found"}
        
        url = lead.get('url')
        if not url:
            return {"error": "Lead has no URL to research"}
        
        print(f"  [Enrichment] Scouting {url}...")
        try:
            enrichment_data = await self.researcher.enrich_lead_data(url)
            
            if enrichment_data:
                # Prepare for DB (serialize lists)
                if enrichment_data.get('intent_signals'):
                    enrichment_data['intent_signals'] = json.dumps(enrichment_data['intent_signals'])
                else:
                    enrichment_data['intent_signals'] = None
                
                # Technographics -> tech_stack
                if enrichment_data.get('technographics'):
                    enrichment_data['tech_stack'] = json.dumps(enrichment_data['technographics'])
                else:
                    enrichment_data['tech_stack'] = None
                
                update_lead_enrichment(lead_id, enrichment_data)
                return {"success": True, "data": enrichment_data}
            else:
                return {"error": "No data returned from researcher"}
        except Exception as e:
            print(f"  [Enrichment] Error enriching {url}: {e}")
            return {"error": str(e)}

    async def batch_enrich_leads(self, lead_ids, concurrency=None):
        """
        Enriches multiple leads in parallel.
        """
        if concurrency is None:
            mode = config.get('project', {}).get('performance_mode', 'paid')
            concurrency = config.get('project', {}).get('concurrency_settings', {}).get(mode, {}).get('scrape', 3)
        semaphore = asyncio.Semaphore(concurrency)
        
        async def sem_enrich(lid):
            async with semaphore:
                return await self.enrich_lead(lid)
        
        tasks = [sem_enrich(lid) for lid in lead_ids]
        return await asyncio.gather(*tasks)
