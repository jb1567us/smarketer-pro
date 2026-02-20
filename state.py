import reflex as rx
import sys
import os
import asyncio
from typing import Any

# Add project root and backend directory to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "backend"))

# Import models and base state
from .models import Message, ChatSession, Lead, Campaign
from .states.base import BaseState, DB_AVAILABLE, engine
from .states.nav import NavState

# Navigation items
NAVIGATION_ITEMS = [
    ("🏠", "Home"),
    ("👥", "Leads"),
    ("🔥", "Campaigns"),
    ("📧", "Sequences"),
    ("📥", "Inbox"),
    ("📊", "Pipeline"),
    ("✅", "Tasks"),
    ("📈", "Analytics"),
    ("⚙️", "Settings"),
    ("🔧", "Mass Tools"),
    ("🤖", "Agent Lab"),
    ("🌐", "Proxy Lab"),
    ("🤖", "Automation Hub"),
    ("🛠️", "Workflow Builder"),
    ("💻", "System Monitor"),
    ("🏭", "Agent Factory"),
    ("🔍", "Direct Search"),
    ("📱", "Social Hub"),
    ("🤝", "Affiliate Hub"),
    ("🏛️", "DSR Manager"),
    ("🎨", "Designer"),
    ("🎬", "Video Studio"),
    ("🚀", "SEO Suite"),
]

class State(NavState):
    """The main entry point for the app state."""
    # Global Dashboard Stats
    total_leads: int = 0
    active_campaigns_count: int = 0
    success_rate: str = "0%"

    async def on_load(self):
        """Called when the app first loads."""
        # 1. Initialize Database immediately if needed
        if DB_AVAILABLE and not self.db_initialized:
            try:
                from backend.database import init_db
                await asyncio.to_thread(init_db)
                self.db_initialized = True
            except Exception as e:
                print(f"CRITICAL: Failed to initialize database: {e}")

        # 2. Robust token retrieval for debug log
        token = "unknown"
        try:
            if hasattr(self, "router") and hasattr(self.router, "session"):
                token = getattr(self.router.session, "id", 
                        getattr(self.router.session, "session_token", 
                        getattr(self.router.session, "token", "unknown")))
            elif hasattr(self, "session"):
                token = getattr(self.session, "id", 
                        getattr(self.session, "session_token", "unknown"))
        except Exception:
            pass
            
        print(f"DEBUG: on_load triggered for session {token}", flush=True)
        from .states.system import HeartbeatState
        yield HeartbeatState.run_heartbeat
        
        # 3. Load Stats (NOW SAFE because tables exist)
        await self.load_dashboard_stats()
        
        # 4. Trigger background poller
        self.is_polling = True
        yield State.start_poller
        
        # 5. Access Proxies (Force hydration of required states)
        from .states.leads import LeadState
        from .states.campaigns import CampaignState
        from .states.inbox import InboxState
        from .states.system import SystemState
        from .states.outreach import SocialState, SEOState
        from .states.creative import CreativeState
        from .states.llm import LLMState
        from .states.portfolio import PortfolioState
        
        async with self:
            self.is_hydrated = True
            lead_state = await self.get_state(LeadState)
            campaign_state = await self.get_state(CampaignState)
            inbox_state = await self.get_state(InboxState)
            system_state = await self.get_state(SystemState)
            social_state = await self.get_state(SocialState)
            creative_state = await self.get_state(CreativeState)
            seo_state = await self.get_state(SEOState)
            llm_state = await self.get_state(LLMState)
            portfolio_state = await self.get_state(PortfolioState)

        if DB_AVAILABLE:
            try:
                from backend.workflow_manager import list_workflows
                await lead_state.load_leads()
                await self.load_dashboard_stats()
                yield
                
                async with system_state:
                    system_state.available_workflows = list_workflows()
                await system_state.update_automation_state()
                await campaign_state.load_campaigns()
                await inbox_state.load_inbox()
                yield SocialState.load_posts
                await creative_state.load_creative_data()
                yield SEOState.load_seo_data
                llm_state.update_router_stats()
                yield LLMState.poll_router_health
                yield PortfolioState.poll_portfolio_metrics
            except Exception as e:
                print(f"Error in on_load initialization: {e}")
        
        pass

    @rx.event(background=True)
    async def start_poller(self):
        """Background task to handle periodic polling across sub-states."""
        from .states.system import SystemState
        while self.is_polling:
            try:
                async with self:
                    system_state = await self.get_state(SystemState)
                await system_state.update_automation_state()
            except Exception as e:
                print(f"Main poller stopped for session: {e}", flush=True)
                break
            await asyncio.sleep(5)

    async def load_dashboard_stats(self):
        """Load dashboard statistics."""
        if DB_AVAILABLE:
            try:
                from backend.database import get_dashboard_stats
                stats = get_dashboard_stats()
                self.total_leads = stats.get('total_leads', 0)
                self.active_campaigns_count = stats.get('active_campaigns', 0)
                success = stats.get('success_rate', 0)
                self.success_rate = f"{int(success * 100)}%" if success else "0%"
            except Exception as e:
                print(f"Error loading stats: {e}")

    # Global UI toggles that didn't fit elsewhere
    def handle_ui_action(self, action: str):
        self.add_log(f"UI Action: {action} (Not implemented in prototype)")
