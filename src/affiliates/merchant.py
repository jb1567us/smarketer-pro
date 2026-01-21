import random
import string
from sqlalchemy.orm import Session
from affiliates.models import Partner, TrackingEvent, Program
from datetime import datetime

class ProgramManager:
    def __init__(self, db: Session):
        self.db = db
        self.program_settings = self._get_or_create_default_program()

    def _get_or_create_default_program(self):
        prog = self.db.query(Program).first()
        if not prog:
            prog = Program(name="Main Program", commission_percentage=20.0)
            self.db.add(prog)
            self.db.commit()
        return prog

    def generate_referral_code(self, base_name: str) -> str:
        """Generates a unique referral code, e.g. 'john20'."""
        clean_name = "".join(e for e in base_name if e.isalnum()).lower()
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
        return f"{clean_name}{suffix}"

    def register_partner(self, user_id: str, email: str, name: str) -> Partner:
        """Onboards a new partner."""
        existing = self.db.query(Partner).filter(Partner.email == email).first()
        if existing:
            return existing

        code = self.generate_referral_code(name)
        partner = Partner(
            user_id=user_id,
            email=email,
            name=name,
            referral_code=code,
            status="active"
        )
        self.db.add(partner)
        self.db.commit()
        return partner

    def generate_partner_link(self, partner_id: int, base_url: str) -> str:
        partner = self.db.query(Partner).get(partner_id)
        if not partner:
            raise ValueError("Partner not found")
        
        # Simple query param style
        separator = "&" if "?" in base_url else "?"
        return f"{base_url}{separator}ref={partner.referral_code}"

    def calculate_commission(self, conversion_amount: float) -> float:
        """Calculates commission based on program settings."""
        rate = self.program_settings.commission_percentage / 100.0
        return round(conversion_amount * rate, 2)

    def delete_partner(self, partner_id: int):
        """Deletes a partner from the system."""
        partner = self.db.query(Partner).get(partner_id)
        if partner:
            self.db.delete(partner)
            self.db.commit()
