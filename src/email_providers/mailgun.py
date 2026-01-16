import os
import requests
from config import config
from .base import EmailProvider

class MailgunProvider(EmailProvider):
    def __init__(self):
        self.api_key = os.getenv("MAILGUN_API_KEY")
        self.domain = os.getenv("MAILGUN_DOMAIN")
        self.from_email = config['email'].get('from_email')
        
        # Region handling could be added (US vs EU), defaulting to US
        self.api_url = f"https://api.mailgun.net/v3/{self.domain}/messages"

    def send_html_email(self, to_email, subject, html_content):
        if not self.api_key or not self.domain:
            print("  [Mailgun] Error: MAILGUN_API_KEY or MAILGUN_DOMAIN not found.")
            return {
                "success": False,
                "provider": "mailgun",
                "message_id": None,
                "metadata": {"error": "Credentials or Domain Missing"}
            }

        try:
            response = requests.post(
                self.api_url,
                auth=("api", self.api_key),
                data={
                    "from": self.from_email,
                    "to": to_email,
                    "subject": subject,
                    "html": html_content
                }
            )
            response.raise_for_status()
            
            data = response.json()
            msg_id = data.get("id")
            
            print(f"  [Mailgun] Email sent to {to_email} (ID: {msg_id})")
            return {
                "success": True,
                "provider": "mailgun",
                "message_id": msg_id,
                "metadata": {"status": response.status_code}
            }
            
        except Exception as e:
            print(f"  [Mailgun] Failed to send to {to_email}: {e}")
            return {
                "success": False,
                "provider": "mailgun",
                "message_id": None,
                "metadata": {"error": str(e)}
            }
