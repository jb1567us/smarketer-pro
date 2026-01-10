import os
import requests
from config import config
from .base import EmailProvider

class SendGridProvider(EmailProvider):
    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = config['email'].get('from_email')
        self.api_url = "https://api.sendgrid.com/v3/mail/send"

    def send_html_email(self, to_email, subject, html_content):
        if not self.api_key:
            print("  [SendGrid] Error: SENDGRID_API_KEY not found.")
            return False

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": self.from_email},
            "subject": subject,
            "content": [{"type": "text/html", "value": html_content}]
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            if response.status_code not in [200, 201, 202]:
                 print(f"  [SendGrid] Error {response.status_code}: {response.text}")
                 return False
            
            print(f"  [SendGrid] Email sent to {to_email}")
            return True
        except Exception as e:
            print(f"  [SendGrid] Failed to send to {to_email}: {e}")
            return False
