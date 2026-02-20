import reflex as rx
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from .base import BaseState, DB_AVAILABLE

class SocialState(BaseState):
    """State for social media scheduling and automation."""
    
    scheduled_posts: List[Dict[str, Any]] = []
    platforms: List[str] = ["LinkedIn", "Twitter", "Instagram", "Threads"]
    selected_platforms: List[str] = []
    post_content: str = ""
    scheduled_date: str = datetime.now().strftime("%Y-%m-%d")
    scheduled_time: str = datetime.now().strftime("%H:%M")
    is_loading: bool = False
    
    async def load_posts(self):
        """Load scheduled posts from the database."""
        if not DB_AVAILABLE:
            self.add_log("Database not available for social posts.")
            return
            
        self.is_loading = True
        yield
        
        try:
            from backend.database import get_scheduled_posts
            self.scheduled_posts = await asyncio.to_thread(get_scheduled_posts, 'pending')
        except Exception as e:
            self.handle_error(e, "Loading Posts")
            
        self.is_loading = False

    async def schedule_post(self):
        """Schedule a new social media post."""
        if not self.post_content or not self.selected_platforms:
            self.handle_error(ValueError("Content and at least one platform required"), "Schedule Post")
            return
            
        if not DB_AVAILABLE:
            self.add_log("Database not available. Post simulations recorded.")
            self.show_success("Post scheduled (Simulated)")
            return
            
        try:
            from backend.database import save_scheduled_post
            
            # Convert date/time to timestamp
            dt_str = f"{self.scheduled_date} {self.scheduled_time}"
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
            ts = int(dt.timestamp())
            
            await asyncio.to_thread(
                save_scheduled_post,
                source="Manual UI",
                platforms=self.selected_platforms,
                content=self.post_content,
                scheduled_ts=ts
            )
            
            self.show_success("Post scheduled successfully.")
            self.post_content = ""
            self.selected_platforms = []
            yield SocialState.load_posts
            
        except Exception as e:
            self.handle_error(e, "Scheduling Post")

    def toggle_platform(self, platform: str):
        """Toggle selected platform."""
        if platform in self.selected_platforms:
            self.selected_platforms.remove(platform)
        else:
            self.selected_platforms.append(platform)

    async def delete_post(self, post_id: int):
        """Delete a scheduled post."""
        if not DB_AVAILABLE: return
        
        try:
            from backend.database import delete_scheduled_post
            await asyncio.to_thread(delete_scheduled_post, post_id)
            yield SocialState.load_posts
        except Exception as e:
            self.handle_error(e, "Deleting Post")

class AffiliateState(BaseState):
    """State for managing affiliate programs and partners."""
    
    my_programs: List[Dict[str, Any]] = []
    my_links: List[Dict[str, Any]] = []
    partners: List[Dict[str, Any]] = []
    
    is_loading: bool = False
    
    async def load_affiliate_data(self):
        """Load all affiliate related data."""
        if not DB_AVAILABLE: return
        
        self.is_loading = True
        yield
        
        try:
            from backend.affiliate_system import AffiliateManager
            am = AffiliateManager()
            self.my_programs = await asyncio.to_thread(am.get_my_programs)
            self.my_links = await asyncio.to_thread(am.get_my_links)
            self.partners = await asyncio.to_thread(am.get_partners)
        except Exception as e:
            self.handle_error(e, "Loading Affiliate Data")
            
        self.is_loading = False

    async def add_program(self, name: str, login_url: str):
        """Add a new affiliate program."""
        if not DB_AVAILABLE: return
        try:
            from backend.affiliate_system import AffiliateManager
            am = AffiliateManager()
            await asyncio.to_thread(am.add_my_program, name, login_url, "", "")
            yield AffiliateState.load_affiliate_data
        except Exception as e:
            self.handle_error(e, "Adding Program")

class DSRState(BaseState):
    """State for Digital Sales Room (DSR) management."""
    
    dsrs: List[Dict[str, Any]] = []
    is_generating: bool = False
    
    async def load_dsrs(self):
        """Fetch all digital sales rooms."""
        if not DB_AVAILABLE: return
        
        try:
            from backend.dsr_manager import DSRManager
            dm = DSRManager()
            self.dsrs = await asyncio.to_thread(dm.get_all_dsrs)
        except Exception as e:
            self.handle_error(e, "Loading DSRs")

    async def generate_dsr(self, campaign_id: int, lead_id: int):
        """Trigger AI generation of a new sales room."""
        if not DB_AVAILABLE:
            self.show_success("Mock DSR Generated (Ready for Preview)")
            return
            
        self.is_generating = True
        yield
        
        try:
            from backend.dsr_manager import DSRManager
            # We'd need to fetch lead_data here from DB
            from backend.database import get_connection
            conn = get_connection()
            conn.row_factory = sqlite3.Row
            lead = conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()
            conn.close()
            
            dm = DSRManager()
            # Original line: await dm.generate_dsr_for_lead(campaign_id, dict(lead) if lead else {})
            # The provided snippet implies a different flow, assuming `dm` returns a result `res`
            # and `self.dsr_title` is set.
            # For consistency with the provided snippet, we'll assume `dm.generate_dsr_for_lead`
            # now returns a result that needs to be saved.
            res = await dm.generate_dsr_for_lead(campaign_id, dict(lead) if lead else {})
            
            await asyncio.to_thread(save_dsr, title=self.dsr_title, content=json.dumps(res))
            yield DSRState.load_dsrs
            
            self.show_success(f"DSR '{self.dsr_title}' generated.")
        except Exception as e:
            self.handle_error(e, "Generating DSR")
            
        self.is_generating_dsr = False # Changed from self.is_generating

class SEOState(BaseState):
    """State for managing SEO audits and keyword research."""
    
    # Audit State
    audit_url: str = ""
    last_audit_report: Dict[str, Any] = {}
    audit_history: List[Dict[str, Any]] = []
    is_auditing: bool = False
    
    # Keyword State
    keyword_topic: str = ""
    last_keyword_report: Dict[str, Any] = {}
    keyword_history: List[Dict[str, Any]] = []
    is_researching: bool = False
    
    # Link Wheel State
    lw_money_site: str = ""
    lw_niche: str = ""
    lw_strategy: str = "Standard Wheel"
    last_lw_plan: Dict[str, Any] = {}

    async def load_seo_data(self):
        """Load SEO history from DB."""
        if not DB_AVAILABLE: return
        try:
            from backend.database import get_seo_audits, get_keyword_reports
            self.audit_history = await asyncio.to_thread(get_seo_audits)
            self.keyword_history = await asyncio.to_thread(get_keyword_reports)
        except Exception as e:
            self.handle_error(e, "Loading SEO Data")

    async def run_audit(self):
        if not self.audit_url:
            self.show_error("Please enter a URL to audit.")
            return

        self.is_auditing = True
        yield
        
        try:
            from backend.agents.seo_agent import SEOExpertAgent
            from backend.database import save_seo_audit
            
            agent = SEOExpertAgent()
            res = await agent.audit_site(self.audit_url)
            self.last_audit_report = res
            
            if DB_AVAILABLE:
                await asyncio.to_thread(
                    save_seo_audit,
                    url=self.audit_url,
                    score=res['report']['site_audit']['score'],
                    metrics=res['metrics'],
                    report=res['report']
                )
                yield SEOState.load_seo_data
                
            self.show_success(f"Audit complete for {self.audit_url}")
        except Exception as e:
            self.handle_error(e, "SEO Audit")
            
        self.is_auditing = False

    async def research_keywords(self):
        if not self.keyword_topic:
            self.show_error("Please enter a topic.")
            return

        self.is_researching = True
        yield
        
        try:
            from backend.agents.seo_agent import SEOExpertAgent
            from backend.database import save_keyword_report
            
            agent = SEOExpertAgent()
            res = await asyncio.to_thread(agent.research_keywords, self.keyword_topic)
            self.last_keyword_report = res
            
            if DB_AVAILABLE:
                await asyncio.to_thread(save_keyword_report, topic=self.keyword_topic, results=res)
                yield SEOState.load_seo_data
                
            self.show_success("Keyword research complete.")
        except Exception as e:
            self.handle_error(e, "Keyword Research")
            
        self.is_researching = False

    async def design_link_wheel(self):
        if not self.lw_money_site or not self.lw_niche:
            self.show_error("Please provide both Money Site URL and Niche.")
            return
            
        try:
            from backend.agents.seo_agent import SEOExpertAgent
            agent = SEOExpertAgent()
            self.last_lw_plan = await asyncio.to_thread(
                agent.design_link_wheel, 
                self.lw_money_site, 
                self.lw_niche, 
                self.lw_strategy
            )
            self.show_success("Link Wheel strategy designed.")
        except Exception as e:
            self.handle_error(e, "Link Wheel Architect")
