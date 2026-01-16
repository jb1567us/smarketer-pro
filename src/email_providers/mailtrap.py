import os
import requests
from config import config
from .base import EmailProvider

class MailtrapProvider(EmailProvider):
    def __init__(self):
        self.api_token = os.getenv("MAILTRAP_API_TOKEN")
        self.from_email = config['email'].get('from_email')
        # Standard Mailtrap Sending API endpoint
        self.api_url = "https://send.api.mailtrap.io/api/send"

    def send_html_email(self, to_email, subject, html_content):
        if not self.api_token:
            print("  [Mailtrap] Error: MAILTRAP_API_TOKEN not found.")
            return {
                "success": False,
                "provider": "mailtrap",
                "message_id": None,
                "metadata": {"error": "API Token Missing"}
            }

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
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
            
            if response.status_code == 200:
                data = response.json()
                # Mailtrap returns distinct message_ids for each recipient
                msg_ids = data.get("message_ids", [])
                msg_id = msg_ids[0] if msg_ids else "sent"
                
                print(f"  [Mailtrap] Email sent to {to_email}")
                return {
                    "success": True,
                    "provider": "mailtrap",
                    "message_id": msg_id,
                    "metadata": {"status": "success"}
                }
            else:
                 print(f"  [Mailtrap] Error: {response.text}")
                 return {
                    "success": False,
                    "provider": "mailtrap",
                    "message_id": None,
                    "metadata": {"error": response.text, "status": response.status_code}
                }

        except Exception as e:
            print(f"  [Mailtrap] Failed to send to {to_email}: {e}")
            return {
                "success": False,
                "provider": "mailtrap",
                "message_id": None,
                "metadata": {"error": str(e)}
            }
