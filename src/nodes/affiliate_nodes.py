from .base import BaseNode
from src.affiliates.manager import OfferManager
from src.affiliates.merchant import ProgramManager
from src.database import get_db_session

class CreateAffiliateOfferNode(BaseNode):
    display_name = "Create Affiliate Offer"
    node_type = "affiliate.offer.create"
    
    async def execute(self, context, params):
        name = params.get("name")
        target_url = params.get("target_url")
        slug = params.get("slug")
        
        with get_db_session() as db:
            mgr = OfferManager(db)
            link = mgr.add_offer(name, target_url, slug)
            return {"offer_id": link.id, "slug": link.slug, "cloaked_url": f"/ref/{slug}"}

class CreatePartnerLinkNode(BaseNode):
    display_name = "Create Partner Link"
    node_type = "affiliate.partner_link.create"
    
    async def execute(self, context, params):
        partner_id = params.get("partner_id")
        base_url = params.get("base_url", "https://smarketer.pro")
        
        with get_db_session() as db:
            mgr = ProgramManager(db)
            url = mgr.generate_partner_link(partner_id, base_url)
            return {"partner_link": url}

class LogAffiliateClickNode(BaseNode):
    display_name = "Log Affiliate Click"
    node_type = "affiliate.click.log"
    
    async def execute(self, context, params):
        # params: source_type, source_id, metadata
        from src.affiliates.tracker import LinkTracker
        with get_db_session() as db:
            tracker = LinkTracker(db)
            vid = tracker.record_click(
                params.get("source_type"),
                params.get("source_id"),
                params.get("metadata")
            )
            return {"visitor_id": vid}
