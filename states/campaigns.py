import reflex as rx
from .base import BaseState, DB_AVAILABLE
from ..models import Campaign

class CampaignState(BaseState):
    """Campaign management state."""
    campaigns: list[Campaign] = []
    active_campaigns_count: int = 0
    selected_campaign: Campaign | None = None
    is_campaign_detail_open: bool = False
    campaign_lead_count: int = 0

    @rx.var
    def success_rate(self) -> str:
        # Placeholder logic for success rate
        return "0%"
    
    # Campaign Creation
    new_campaign_name: str = ""
    new_campaign_niche: str = ""
    new_campaign_product_name: str = ""
    new_campaign_product_context: str = ""
    is_creating_campaign: bool = False
    campaign_creation_error: str = ""

    async def load_campaigns(self):
        """Load campaigns from database."""
        if DB_AVAILABLE:
            try:
                from backend.database import get_all_campaigns
                raw_campaigns = get_all_campaigns()
                async with self:
                    self.campaigns = [Campaign(**c) for c in raw_campaigns]
                    self.active_campaigns_count = len([c for c in self.campaigns if c.status == "active"])
            except Exception as e:
                print(f"Error loading campaigns: {e}")

    async def select_campaign(self, campaign: Campaign):
        """Open campaign detail view."""
        self.selected_campaign = campaign
        self.is_campaign_detail_open = True
        
        if DB_AVAILABLE:
            try:
                from backend.database import get_campaign_leads_count
                self.campaign_lead_count = get_campaign_leads_count(campaign.id)
            except Exception as e:
                print(f"Error loading campaign stats: {e}")
                self.campaign_lead_count = 0

    def close_campaign_detail(self):
        """Close campaign detail view."""
        self.is_campaign_detail_open = False
        self.selected_campaign = None

    async def create_new_campaign(self):
        """Create a new mission/campaign."""
        if not self.new_campaign_name:
            self.campaign_creation_error = "Campaign name is required"
            return
        
        self.is_creating_campaign = True
        self.campaign_creation_error = ""
        yield
        
        if DB_AVAILABLE:
            try:
                from backend.database import create_campaign
                campaign_data = {
                    "name": self.new_campaign_name,
                    "niche": self.new_campaign_niche,
                    "product_name": self.new_campaign_product_name,
                    "product_context": self.new_campaign_product_context,
                    "status": "active"
                }
                create_campaign(campaign_data)
                self.add_log(f"Created campaign: {self.new_campaign_name}")
                self.new_campaign_name = ""
                self.new_campaign_niche = ""
                await self.load_campaigns()
            except Exception as e:
                self.campaign_creation_error = f"Error: {e}"
        else:
            await asyncio.sleep(1)
            self.add_log(f"Prototype: Created campaign {self.new_campaign_name}")
            self.new_campaign_name = ""
            
        self.is_creating_campaign = False

    def get_campaign_status_color(self, status):
        return "green" if status == "active" else "gray"
