import uuid
import base64
from datetime import datetime
from database import get_connection

class AnalyticsBridge:
    def __init__(self):
        self.pixel_base_url = "https://api.smarketer-pro.com/track/open" # Virtual endpoint
        self.link_base_url = "https://api.smarketer-pro.com/track/click" # Virtual endpoint

    def generate_tracking_pixel(self, campaign_id, lead_id):
        """
        Creates a 1x1 invisible pixel with encoded metadata.
        """
        payload = f"{campaign_id}:{lead_id}"
        encoded = base64.urlsafe_b64encode(payload.encode()).decode()
        url = f"{self.pixel_base_url}?id={encoded}"
        return f'<img src="{url}" width="1" height="1" style="display:none;" alt="" />'

    def rewrite_links(self, html_content, campaign_id, lead_id):
        """
        Parses HTML and wraps all <a> tags with tracking redirects.
        (Simplified implementation for regex/string replacement)
        """
        # In a real impl, we'd use BeautifulSoup to find all 'a' hrefs
        # and replace them with self.link_base_url?redirect=...&meta=...
        # For simulation, we'll just track that we WOULDA done it.
        return html_content # Returning as-is for this mockup, logic is placeholder

    def record_event(self, event_type, campaign_id, lead_id, meta=None):
        """
        Logs an event (open, click, reply) to the database.
        """
        # This would typically be called by the API endpoint receiving the pixel/click request
        # Here we simulate the DB recording directly
        print(f"[Analytics] Recording {event_type} for Campaign {campaign_id}, Lead {lead_id}")
        # Insert into a new 'analytics_events' table (which we'd need to create)
        # Fetch lead to get email
        from database import get_lead_by_id, log_campaign_event
        lead = get_lead_by_id(lead_id)
        email = lead['email'] if lead else 'unknown'
        
        log_campaign_event(
            email=email, 
            event_type=event_type, 
            lead_id=lead_id, 
            campaign_id=campaign_id,
            event_data=meta
        )

    def get_campaign_performance(self, campaign_id):
        """
        Returns aggregated metrics for a campaign to feed into agents.
        """
        # Mock logic based on stored data
        # In reality, query DB: SELECT count(*) FROM analytics_events WHERE ...
        return {
            "sent": 100,
            "opens": 45,
            "clicks": 12,
            "replies": 3,
            "open_rate": 0.45,
            "click_rate": 0.12,
            "top_performing_subject": "Quick question about {company}",
            "worst_performing_subject": "Touching base"
        }

analytics_bridge = AnalyticsBridge()
