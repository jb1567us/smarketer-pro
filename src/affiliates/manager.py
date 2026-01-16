from sqlalchemy.orm import Session
from affiliates.models import AffiliateLink
from sqlalchemy import or_

class OfferManager:
    def __init__(self, db: Session):
        self.db = db

    def add_offer(self, name: str, target_url: str, slug: str, program_name: str = None, commission_rate: str = None) -> AffiliateLink:
        """
        Registers a new affiliate link to promote.
        """
        existing = self.db.query(AffiliateLink).filter(AffiliateLink.slug == slug).first()
        if existing:
            raise ValueError(f"Slug '{slug}' is already in use.")

        link = AffiliateLink(
            name=name,
            target_url=target_url,
            slug=slug,
            program_name=program_name,
            commission_rate=commission_rate
        )
        self.db.add(link)
        self.db.commit()
        return link

    def get_best_offer(self, keyword: str) -> AffiliateLink:
        """
        Finds the most relevant affiliate link for a given keyword/topic.
        Simple partial match on name or program_name.
        """
        # Improved logic could use semantic search, but simple SQL LIKE is checking basics first
        link = self.db.query(AffiliateLink).filter(
            or_(
                AffiliateLink.name.ilike(f"%{keyword}%"),
                AffiliateLink.program_name.ilike(f"%{keyword}%")
            ),
            AffiliateLink.is_active == True
        ).first()
        
        return link

    def list_offers(self):
        """Returns all active offers."""
        return self.db.query(AffiliateLink).filter(AffiliateLink.is_active == True).all()
