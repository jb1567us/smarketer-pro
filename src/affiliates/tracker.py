import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from src.affiliates.models import TrackingEvent, AffiliateLink, Partner

class LinkTracker:
    def __init__(self, db: Session):
        self.db = db

    def record_click(self, source_type: str, source_id: str, metadata: dict = None, visitor_id: str = None) -> str:
        """
        Logs a click event.
        source_type: 'publisher' (we link out) or 'merchant' (partner links in)
        source_id: AffiliateLink.id or Partner.id
        """
        if not visitor_id:
            visitor_id = str(uuid.uuid4())

        event = TrackingEvent(
            event_type="click",
            source_id=f"{source_type}:{source_id}",
            timestamp=datetime.utcnow(),
            metadata_json=metadata or {},
            visitor_id=visitor_id
        )
        self.db.add(event)
        self.db.commit()
        return visitor_id

    def get_cloaked_url(self, slug: str) -> str:
        """
        Returns the target URL for a given slug, or None if not found.
        """
        link = self.db.query(AffiliateLink).filter(AffiliateLink.slug == slug).first()
        if link and link.is_active:
            return link.target_url
        return None

    def resolve_referral_code(self, code: str) -> Partner:
        """
        Finds a partner by referral code.
        """
        return self.db.query(Partner).filter(Partner.referral_code == code, Partner.status == "active").first()

    def record_conversion(self, visitor_id: str, amount: float, metadata: dict = None):
        """
        Attributes a conversion to a past click/visitor.
        """
        # 1. Find the last 'merchant' click for this visitor
        # Usage of like check for 'merchant:%' is simple logic, might need refinement
        last_click = self.db.query(TrackingEvent)\
            .filter(TrackingEvent.visitor_id == visitor_id)\
            .filter(TrackingEvent.event_type == "click")\
            .filter(TrackingEvent.source_id.like("merchant:%"))\
            .order_by(TrackingEvent.timestamp.desc())\
            .first()

        partner_id = None
        if last_click:
            # Parse partner ID from source_id "merchant:123"
            try:
                partner_id = int(last_click.source_id.split(":")[1])
            except (IndexError, ValueError):
                pass

        conversion = TrackingEvent(
            event_type="conversion",
            source_id=last_click.source_id if last_click else "direct",
            timestamp=datetime.utcnow(),
            metadata_json=metadata or {},
            value=amount,
            visitor_id=visitor_id,
            partner_id=partner_id
        )
        self.db.add(conversion)
        self.db.commit()
        return conversion
