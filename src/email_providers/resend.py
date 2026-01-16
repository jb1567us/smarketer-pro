import os
import requests
from config import config
from .base import EmailProvider

class ResendProvider(EmailProvider):
    def __init__(self):
        self.api_key = os.getenv("RESEND_API_KEY")
        # Fallback format: config['email']['from_email'] 
        self.from_email = config['email'].get('from_email', 'onboarding@resend.dev')
        self.api_url = 'https://api.resend.com/emails'

    def send_html_email(self, to_email, subject, html_content):
        if not self.api_key:
            print("  [Resend] Error: RESEND_API_KEY not found.")
            return {
                "success": False,
                "provider": "resend",
                "message_id": None,
                "metadata": {"error": "API Key Missing"}
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "from": self.from_email,
            "to": [to_email],
            "subject": subject,
            "html": html_content
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            msg_id = response.json().get('id')
            print(f"  [Resend] Email sent to {to_email} (ID: {msg_id})")
            return {
                "success": True,
                "provider": "resend",
                "message_id": msg_id,
                "metadata": {"status": response.status_code}
            }
        except Exception as e:
            print(f"  [Resend] Failed to send to {to_email}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"  [Resend] Response: {e.response.text}")
            return {
                "success": False,
                "provider": "resend",
                "message_id": None,
                "metadata": {"error": str(e)}
            }
