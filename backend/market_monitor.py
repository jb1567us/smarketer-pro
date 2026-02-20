import asyncio
import logging
import time
from typing import List, Dict
from backend.database import get_connection
from backend.agents.intelligence import MarketIntelligenceAgent
from backend.stealth_utils import search_rotator, searx_provider

# Configure logging
logger = logging.getLogger(__name__)

class MarketMonitor:
    """
    Orchestrates periodic market intelligence scans using rotated search backends.
    """
    _instance = None

    def __init__(self):
        self.agent = MarketIntelligenceAgent()
        self.is_running = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def run_market_check(self, niche: str):
        """
        Executes a single market scan for a niche.
        """
        try:
            route = search_rotator.get_best_route()
            logger.info(f"Running market check for '{niche}' via {route}...")

            # 1. Perform Search (Mocked for Prototype)
            # In a real scenario, this would use a SearXNG or Google Search API
            mock_snippets = [
                {
                    "title": f"New Competitor in {niche} Industry",
                    "snippet": f"A new startup just launched a disruptive tool for the {niche} market.",
                    "source": "TechNews"
                },
                {
                    "title": f"{niche} Market Trends for 2026",
                    "snippet": f"Recent regulatory changes are affecting How {niche} professionals work.",
                    "source": "Industry Weekly"
                }
            ]
            
            # 2. Distill News via Agent
            events = await self.agent.distill_news(niche, mock_snippets)
            
            # 3. Store in DB
            conn = get_connection()
            c = conn.cursor()
            
            new_count = 0
            for event in events:
                # Deduplication check
                c.execute("SELECT 1 FROM market_events WHERE headline = ? AND niche = ?", 
                         (event.get("headline"), niche))
                if not c.fetchone():
                    c.execute('''
                        INSERT INTO market_events 
                        (niche, source, headline, summary, sentiment, strategic_hook, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        niche, 
                        "Automated Scan", 
                        event.get("headline"), 
                        event.get("summary"), 
                        event.get("sentiment"), 
                        event.get("strategic_hook"),
                        int(time.time())
                    ))
                    new_count += 1
            
            conn.commit()
            conn.close()
            
            logger.info(f"Market check complete for {niche}. Found {new_count} new events.")
            return new_count

        except Exception as e:
            logger.error(f"Market check error for {niche}: {e}")
            return 0

    async def start_monitoring_loop(self):
        """Background loop for continuous intelligence gathering."""
        self.is_running = True
        niches = ["Plumbing", "Roofing", "HVAC"] # Mock list
        
        while self.is_running:
            for niche in niches:
                await self.run_market_check(niche)
                await asyncio.sleep(60) # Interval between niches
            
            await asyncio.sleep(3600) # Wait an hour between full cycles

if __name__ == "__main__":
    monitor = MarketMonitor.get_instance()
    asyncio.run(monitor.run_market_check("B2B SaaS"))
