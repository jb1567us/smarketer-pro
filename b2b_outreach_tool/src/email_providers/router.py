from config import config
from .base import EmailProvider

# Providers
from .resend import ResendProvider
from .brevo import BrevoProvider
from .sendgrid import SendGridProvider
from .smtp import SMTPProvider

class SmartEmailRouter(EmailProvider):
    def __init__(self):
        # Initialize all potential providers
        self.providers = []
        
        # Load priority list from config or default
        priority_list = config.get('email', {}).get('smart_routing', {}).get('providers', ['resend', 'brevo', 'sendgrid', 'smtp'])
        
        print(f"  [SmartRouter] Initializing providers in order: {priority_list}")
        
        for name in priority_list:
            if name == 'resend': self.providers.append(('Resend', ResendProvider()))
            elif name == 'brevo': self.providers.append(('Brevo', BrevoProvider()))
            elif name == 'sendgrid': self.providers.append(('SendGrid', SendGridProvider()))
            elif name == 'smtp': self.providers.append(('SMTP', SMTPProvider()))

    def send_html_email(self, to_email, subject, html_content):
        # Smart Failover Logic
        for name, provider in self.providers:
            # Try sending
            success = provider.send_html_email(to_email, subject, html_content)
            if success:
                print(f"  [SmartRouter] Delivery successful via {name}.")
                return True
            else:
                print(f"  [SmartRouter] {name} failed. Failing over to next provider...")
        
        print("  [SmartRouter] All providers failed.")
        return False
