import os
import requests
from config import config
from .base import EmailProvider

class BrevoProvider(EmailProvider):
    def __init__(self):
        self.api_key = os.getenv("BREVO_API_KEY")
        self.from_email = config['email'].get('from_email')
        self.api_url = "https://api.brevo.com/v3/smtp/email"

    def send_html_email(self, to_email, subject, html_content):
        if not self.api_key:
            print("  [Brevo] Error: BREVO_API_KEY not found.")
            return False

        headers = {
            "accept": "application/json",
            "api-key": self.api_key,
            "content-type": "application/json"
        }
        
        payload = {
            "sender": {"email": self.from_email},
            "to": [{"email": to_email}],
            "subject": subject,
            "htmlContent": html_content
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            print(f"  [Brevo] Email sent to {to_email}")
            return True
        except Exception as e:
            print(f"  [Brevo] Failed to send to {to_email}: {e}")
            return False
