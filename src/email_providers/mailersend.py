import os
import requests
from config import config
from .base import EmailProvider

class MailerSendProvider(EmailProvider):
    def __init__(self):
        self.api_key = os.getenv("MAILERSEND_API_KEY")
        self.from_email = config['email'].get('from_email')
        self.api_url = "https://api.mailersend.com/v1/email"

    def send_html_email(self, to_email, subject, html_content):
        if not self.api_key:
            print("  [MailerSend] Error: MAILERSEND_API_KEY not found.")
            return {
                "success": False,
                "provider": "mailersend",
                "message_id": None,
                "metadata": {"error": "API Key Missing"}
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest"
        }
        
        payload = {
            "from": {
                "email": self.from_email,
                "name": "Smarketer Pro"
            },
            "to": [
                {
                    "email": to_email
                }
            ],
            "subject": subject,
            "html": html_content
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            
            if response.status_code == 202: # Accepted
                # MailerSend returns ID in header 'X-Message-Id' usually
                msg_id = response.headers.get("X-Message-Id", "queued")
                print(f"  [MailerSend] Email sent to {to_email}")
                return {
                    "success": True,
                    "provider": "mailersend",
                    "message_id": msg_id,
                    "metadata": {"status": "accepted"}
                }
            else:
                print(f"  [MailerSend] Error: {response.text}")
                return {
                    "success": False,
                    "provider": "mailersend",
                    "message_id": None,
                    "metadata": {"error": response.text, "status": response.status_code}
                }

        except Exception as e:
            print(f"  [MailerSend] Failed to send to {to_email}: {e}")
            return {
                "success": False,
                "provider": "mailersend",
                "message_id": None,
                "metadata": {"error": str(e)}
            }
