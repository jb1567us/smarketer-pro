"""
Analytics State

Comprehensive analytics and reporting
"""
import reflex as rx
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json


class AnalyticsState(rx.State):
    """State for analytics dashboard"""
    
    # Date range
    date_from: str = ""
    date_to: str = ""
    
    # Aggregated metrics
    total_campaigns: int = 0
    total_leads: int = 0
    total_emails_sent: int = 0
    avg_response_rate: float = 0.0
    total_llm_cost: float = 0.0
    
    # Campaign performance
    campaign_metrics: List[Dict[str, Any]] = []
    
    # Lead analytics
    lead_status_distribution: Dict[str, int] = {}
    lead_source_distribution: Dict[str, int] = {}
    
    # Email performance
    email_open_rate: float = 0.0
    email_click_rate: float = 0.0
    email_response_rate: float = 0.0
    
    # LLM cost breakdown
    llm_cost_by_provider: Dict[str, float] = {}
    llm_tokens_used: int = 0
    
    # Time series data
    daily_metrics: List[Dict[str, Any]] = []
    
    # Top performers
    top_campaigns: List[Dict[str, Any]] = []
    top_industries: List[Dict[str, Any]] = []
    
    def load_analytics(self):
        """Load all analytics data"""
        from backend.database import Database
        
        db = Database()
        
        # Load campaigns and leads
        campaigns = db.get_all_campaigns()
        leads = db.get_all_leads()
        
        # Calculate totals
        self.total_campaigns = len(campaigns)
        self.total_leads = len(leads)
        
        # Calculate campaign metrics
        self.campaign_metrics = []
        for campaign in campaigns:
            metrics = self._calculate_campaign_metrics(campaign, leads)
            self.campaign_metrics.append(metrics)
        
        # Lead status distribution
        self.lead_status_distribution = {}
        for lead in leads:
            status = lead.get("status", "unknown")
            self.lead_status_distribution[status] = \
                self.lead_status_distribution.get(status, 0) + 1
        
        # Lead source distribution
        self.lead_source_distribution = {}
        for lead in leads:
            source = lead.get("source", "unknown")
            self.lead_source_distribution[source] = \
                self.lead_source_distribution.get(source, 0) + 1
        
        # Email performance (mock data for demo)
        self.email_open_rate = 0.45  # 45%
        self.email_click_rate = 0.12  # 12%
        self.email_response_rate = 0.08  # 8%
        
        # LLM costs (mock data)
        self.llm_cost_by_provider = {
            "OpenAI": 12.50,
            "Anthropic": 8.75,
            "Groq": 2.30
        }
        self.llm_tokens_used = 125000
        self.total_llm_cost = sum(self.llm_cost_by_provider.values())
        
        # Top campaigns
        sorted_campaigns = sorted(
            self.campaign_metrics,
            key=lambda x: x.get("response_rate", 0),
            reverse=True
        )
        self.top_campaigns = sorted_campaigns[:5]
        
        # Generate daily metrics (last 30 days)
        self._generate_daily_metrics()
    
    def _calculate_campaign_metrics(
        self,
        campaign: Dict[str, Any],
        all_leads: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate metrics for a campaign"""
        campaign_id = campaign.get("id")
        
        # Get leads for this campaign
        campaign_leads = [
            lead for lead in all_leads
            if lead.get("campaign_id") == campaign_id
        ]
        
        total_leads = len(campaign_leads)
        sent = sum(1 for l in campaign_leads if l.get("email_sent"))
        opened = sum(1 for l in campaign_leads if l.get("email_opened"))
        responded = sum(1 for l in campaign_leads if l.get("responded"))
        
        return {
            "id": campaign_id,
            "name": campaign.get("name", "Unnamed"),
            "total_leads": total_leads,
            "emails_sent": sent,
            "open_rate": (opened / sent * 100) if sent > 0 else 0,
            "response_rate": (responded / sent * 100) if sent > 0 else 0,
            "status": campaign.get("status", "draft")
        }
    
    def _generate_daily_metrics(self):
        """Generate daily metrics for time series"""
        self.daily_metrics = []
        
        # Generate last 30 days
        for i in range(30, 0, -1):
            date = datetime.now() - timedelta(days=i)
            
            # Mock data with some variance
            import random
            self.daily_metrics.append({
                "date": date.strftime("%Y-%m-%d"),
                "leads_added": random.randint(5, 25),
                "emails_sent": random.randint(10, 50),
                "responses": random.randint(1, 10),
                "llm_cost": random.uniform(0.5, 3.0)
            })
    
    def export_analytics_csv(self):
        """Export analytics to CSV"""
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "Campaign",
            "Total Leads",
            "Emails Sent",
            "Open Rate (%)",
            "Response Rate (%)",
            "Status"
        ])
        
        # Data
        for campaign in self.campaign_metrics:
            writer.writerow([
                campaign["name"],
                campaign["total_leads"],
                campaign["emails_sent"],
                f"{campaign['open_rate']:.1f}",
                f"{campaign['response_rate']:.1f}",
                campaign["status"]
            ])
        
        return output.getvalue()
    
    def export_analytics_json(self):
        """Export analytics to JSON"""
        data = {
            "summary": {
                "total_campaigns": self.total_campaigns,
                "total_leads": self.total_leads,
                "avg_response_rate": self.avg_response_rate,
                "total_llm_cost": self.total_llm_cost
            },
            "campaigns": self.campaign_metrics,
            "lead_distribution": {
                "by_status": self.lead_status_distribution,
                "by_source": self.lead_source_distribution
            },
            "email_performance": {
                "open_rate": self.email_open_rate,
                "click_rate": self.email_click_rate,
                "response_rate": self.email_response_rate
            },
            "llm_costs": self.llm_cost_by_provider,
            "daily_metrics": self.daily_metrics
        }
        
        return json.dumps(data, indent=2)
    
    @rx.var
    def avg_cost_per_lead(self) -> float:
        """Calculate average cost per lead"""
        if self.total_leads > 0:
            return self.total_llm_cost / self.total_leads
        return 0.0
    
    @rx.var
    def roi_estimate(self) -> float:
        """Estimate ROI (mock calculation)"""
        # Assuming $100 value per response
        revenue = self.total_leads * (self.avg_response_rate / 100) * 100
        cost = self.total_llm_cost
        
        if cost > 0:
            return ((revenue - cost) / cost) * 100
        return 0.0
