import os
import requests
from config import config
from .base import EmailProvider

class PostmarkProvider(EmailProvider):
    def __init__(self):
        self.api_key = os.getenv("POSTMARK_API_KEY") # Server Token
        self.from_email = config['email'].get('from_email')
        self.api_url = "https://api.postmarkapp.com/email"

    def send_html_email(self, to_email, subject, html_content):
        if not self.api_key:
            print("  [Postmark] Error: POSTMARK_API_KEY not found.")
            return {
                "success": False,
                "provider": "postmark",
                "message_id": None,
                "metadata": {"error": "API Key Missing"}
            }

        headers = {
            "X-Postmark-Server-Token": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "From": self.from_email,
            "To": to_email,
            "Subject": subject,
            "HtmlBody": html_content,
            "MessageStream": "outbound" # Default stream
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            msg_id = data.get("MessageID")
            
            print(f"  [Postmark] Email sent to {to_email} (ID: {msg_id})")
            return {
                "success": True,
                "provider": "postmark",
                "message_id": msg_id,
                "metadata": {"status": "success"}
            }
            
        except Exception as e:
            print(f"  [Postmark] Failed to send to {to_email}: {e}")
            return {
                "success": False,
                "provider": "postmark",
                "message_id": None,
                "metadata": {"error": str(e)}
            }
