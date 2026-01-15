from abc import ABC, abstractmethod

class PaymentAdapter(ABC):
    @abstractmethod
    def onboard_partner(self, partner_id: str, email: str) -> str:
        """Returns a URL for the partner to set up payouts."""
        pass

    @abstractmethod
    def process_payout(self, partner_id: str, amount: float, currency: str = "usd") -> dict:
        """Executes a payout."""
        pass

class ManualAdapter(PaymentAdapter):
    def onboard_partner(self, partner_id: str, email: str) -> str:
        return "mailto:admin@example.com?subject=Payout%20Setup"

    def process_payout(self, partner_id: str, amount: float, currency: str = "usd") -> dict:
        return {"status": "manual_review", "id": "manual_tx"}

class StripeAdapter(PaymentAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        # import stripe
        # stripe.api_key = self.api_key

    def onboard_partner(self, partner_id: str, email: str) -> str:
        # Mock implementation: in real world, creates a tailored Connect Express account link
        return f"https://connect.stripe.com/express/oauth/authorize?client_id=ca_123&state={partner_id}"

    def process_payout(self, partner_id: str, amount: float, currency: str = "usd") -> dict:
        # Mock implementation: Stripe Transfer logic
        return {"status": "success", "id": "tr_mock_12345"}
