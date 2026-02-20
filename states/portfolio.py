import reflex as rx
import asyncio
from typing import Dict, List, Any
from .base import BaseState
from backend.database import get_connection

class PortfolioState(BaseState):
    """Reflex state for Pillar 3: Content Layer and pSEO Factory."""
    
    total_profiles: int = 0
    high_authority_count: int = 0
    pillar_distribution: Dict[str, float] = {"DSR": 20.0, "Authority": 10.0, "Traffic": 70.0}
    
    # Portfolio interlinking map visualization
    is_generating_map: bool = False
    interlinking_score: int = 85
    
    # Lists for UI
    enriched_profiles: List[Dict[str, Any]] = []
    market_events: List[Dict[str, Any]] = []
    is_scanning_market: bool = False

    @rx.event(background=True)
    async def poll_portfolio_metrics(self):
        """Update portfolio stats from DB."""
        from .video import VideoState
        from .crm import CRMState
        from .content import ContentState
        import json

        while self.is_polling:
            try:
                # Retrieve all required state proxies safely
                async with self:
                    video_st = await self.get_state(VideoState)
                    crm_st = await self.get_state(CRMState)
                    content_st = await self.get_state(ContentState)

                from backend.database import get_connection
                conn = get_connection()
                c = conn.cursor()
                
                # Portfolio Stats
                c.execute("SELECT COUNT(*) FROM company_profiles")
                total_profiles = c.fetchone()[0]
                
                c.execute("SELECT COUNT(*) FROM company_profiles WHERE reputation_score > 90")
                high_authority_count = c.fetchone()[0]
                
                # Fetch recent profiles
                c.execute("SELECT name, city, reputation_score FROM company_profiles ORDER BY created_at DESC LIMIT 5")
                enriched_profiles = [
                    {"name": r[0], "city": r[1], "score": r[2]} 
                    for r in c.fetchall()
                ]
                
                # Fetch recent market events (Phase 5)
                c.execute("SELECT headline, niche, sentiment, strategic_hook FROM market_events ORDER BY timestamp DESC LIMIT 3")
                market_events = [
                    {"headline": r[0], "niche": r[1], "sentiment": r[2], "hook": r[3]}
                    for r in c.fetchall()
                ]
                
                # Update Video Lab Status (Phase 6)
                c.execute("SELECT id, lead_name, script, status, video_url, timestamp FROM video_jobs ORDER BY timestamp DESC LIMIT 3")
                video_queue = [
                    {"id": r[0], "lead_name": r[1], "script": r[2], "status": r[3], "url": r[4], "ts": r[5]}
                    for r in c.fetchall()
                ]
                
                # Update CRM Sync Logs (Phase 7)
                c.execute('''
                    SELECT l.id, p.name, l.provider, l.status, l.timestamp 
                    FROM crm_sync_log l
                    JOIN company_profiles p ON l.lead_id = p.id
                    ORDER BY l.timestamp DESC LIMIT 3
                ''')
                sync_logs = [
                    {"id": r[0], "name": r[1], "provider": r[2], "status": r[3], "ts": r[4]}
                    for r in c.fetchall()
                ]

                # Update Content Assets (Phase 9)
                c.execute('''
                    SELECT id, lead_id, asset_type, layout_json, status, timestamp 
                    FROM content_assets 
                    ORDER BY timestamp DESC LIMIT 3
                ''')
                asset_gallery = [
                    {
                        "id": r[0], "lead_id": r[1], "type": r[2], 
                        "layout": json.loads(r[3]), "status": r[4], "ts": r[5]
                    } for r in c.fetchall()
                ]

                # Auto-Trigger CRM Sync for High Authority (Phase 7)
                high_auth_lead_data = None
                async with crm_st:
                    if crm_st.auto_sync_enabled and not crm_st.is_syncing:
                        c.execute('''
                            SELECT id, name, niche, city, reputation_score 
                            FROM company_profiles 
                            WHERE reputation_score > 90 
                            AND id NOT IN (SELECT lead_id FROM crm_sync_log WHERE status = 'success')
                            LIMIT 1
                        ''')
                        row = c.fetchone()
                        if row:
                            high_auth_lead_data = {
                                "id": row[0], "name": row[1], 
                                "niche": row[2], "city": row[3], 
                                "reputation_score": row[4]
                            }
                
                if high_auth_lead_data:
                    # Sync individual lead is an async event, calling it on the proxy
                    await crm_st.sync_individual_lead(high_auth_lead_data)

                conn.close()
                
                # Push updates to state
                async with self:
                    self.total_profiles = total_profiles
                    self.high_authority_count = high_authority_count
                    self.enriched_profiles = enriched_profiles
                    self.market_events = market_events
                
                # Update sub-states individually
                if video_queue:
                    async with video_st:
                        video_st.video_queue = video_queue
                
                if sync_logs:
                    async with crm_st:
                        crm_st.sync_logs = sync_logs
                
                if asset_gallery:
                    async with content_st:
                        content_st.asset_gallery = asset_gallery

            except Exception as e:
                # Log the specific line where it might be failing if possible, or just the error
                import traceback
                print(f"Portfolio polling error: {e}")
                traceback.print_exc()
            
            await asyncio.sleep(10)

    async def run_market_scan_now(self):
        """Manually trigger Phase 5 intelligence gathering."""
        self.is_scanning_market = True
        self.add_log("Initiating MarketMind Deep Scan (SearXNG + Intelligence Agent)...")
        yield
        
        from backend.market_monitor import MarketMonitor
        monitor = MarketMonitor.get_instance()
        # Scan for existing niches in the tool
        found = await monitor.run_market_check("B2B Tech")
        
        self.is_scanning_market = False
        self.add_log(f"Market Scan Complete. Found {found} new strategic events.")
        yield

    async def run_factory_sync(self):
        """Sync raw leads into the content layer."""
        self.is_generating_map = True
        self.add_log("Starting Site Factory Sync (Leads -> Content Layer)...")
        yield
        
        # Simulate generating a batch of profiles
        from backend.portfolio_utils import sync_profile
        mock_leads = [
            ("Apex Roofing", "Roofers", "Austin", 120, 4.8),
            ("Zen Gardens", "Landscaping", "Denver", 85, 4.9),
            ("Blue Sky Solar", "Solar", "Phoenix", 250, 4.4)
        ]
        
        for name, n, city, r, a in mock_leads:
            score = sync_profile(name, n, city, r, a)
            self.add_log(f"Enriched: {name} (Auth Score: {score})")
            await asyncio.sleep(0.5)
            yield
            
        self.is_generating_map = False
        self.add_log("Site Factory Sync Complete. 3 new profiles added to Pillar 3.")
        yield

    async def generate_video_for_lead(self, lead_name: str):
        """Trigger personalization for a specific high-authority lead."""
        from .video import VideoState
        video_st = await self.get_state(VideoState)
        
        # Fetch lead details from DB
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT name, niche, city, reputation_score FROM company_profiles WHERE name = ?", (lead_name,))
        row = c.fetchone()
        conn.close()
        
        if row:
            lead_data = {"name": row[0], "niche": row[1], "city": row[2], "reputation_score": row[3]}
            await video_st.create_video_job(lead_data)
        else:
            self.add_log(f"❌ Lead {lead_name} not found for video generation.")
        yield

    async def design_carousel_for_lead(self, lead_name: str):
        """Trigger carousel design for a specific lead."""
        from .content import ContentState
        content_st = await self.get_state(ContentState)
        
        # Fetch lead details from DB
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT id, name, niche, city, reputation_score FROM company_profiles WHERE name = ?", (lead_name,))
        row = c.fetchone()
        conn.close()
        
        if row:
            lead_data = {"id": row[0], "name": row[1], "niche": row[2], "city": row[3], "reputation_score": row[4]}
            await content_st.create_carousel_for_lead(lead_data)
        else:
            self.add_log(f"❌ Lead {lead_name} not found for content design.")
        yield

    @rx.var
    def pillar_distribution_list(self) -> List[Dict[str, Any]]:
        return [{"pillar": k, "percentage": v} for k, v in self.pillar_distribution.items()]
