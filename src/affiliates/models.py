from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base

class AffiliateLink(Base):
    """
    Represents an external affiliate OFFER that the user is promoting (Publisher side).
    Example: Promoting 'ConvertKit' to earn commissions.
    """
    __tablename__ = 'affiliate_links'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # e.g. "ConvertKit"
    target_url = Column(String, nullable=False)  # Actual affiliate link with params
    slug = Column(String, unique=True, nullable=False)  # e.g. "convertkit" for domain.com/ref/convertkit
    program_name = Column(String)  # e.g. "PartnerStack"
    commission_rate = Column(String)  # e.g. "30%" or "$20 flat"
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Program(Base):
    """
    Represents the internal affiliate PROGRAM settings (Merchant side).
    Rules for how partners get paid for promoting US.
    """
    __tablename__ = 'affiliate_programs'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="Default Program")
    cookie_window_days = Column(Integer, default=30)
    commission_percentage = Column(Float, default=20.0) # 20% default
    is_active = Column(Boolean, default=True)
    
class Partner(Base):
    """
    Represents a third-party partner who promotes US (Merchant side).
    """
    __tablename__ = 'partners'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, nullable=False) # Link to local User table if exists, or email
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    stripe_connect_id = Column(String, nullable=True) # For payouts
    status = Column(String, default="pending") # pending, active, suspended
    referral_code = Column(String, unique=True, nullable=False) # e.g. "johndoe20"
    created_at = Column(DateTime, default=datetime.utcnow)

class TrackingEvent(Base):
    """
    Unified ledger for all affiliate events (Clicks, Conversions, Payouts).
    """
    __tablename__ = 'tracking_events'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False) # click, lead, conversion, refund, payout
    
    # Polymorphic source: could differ based on event type
    source_id = Column(String, nullable=True) # e.g. AffiliateLink.id OR Partner.id
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(JSON, default={}) # Stores user_agent, ip, referer, etc.
    value = Column(Float, nullable=True) # Monetary value for conversions/payouts
    
    # Attribution
    visitor_id = Column(String, nullable=True) # Cookie ID
    partner_id = Column(Integer, ForeignKey('partners.id'), nullable=True)
    
    partner = relationship("Partner")
