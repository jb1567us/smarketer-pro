import os
import requests
from config import config
from .base import EmailProvider

class NetcoreProvider(EmailProvider):
    def __init__(self):
        self.api_key = os.getenv("NETCORE_API_KEY")
        self.from_email = config['email'].get('from_email')
        self.api_url = "https://api.pepipost.com/v5.1/mail/send"

    def send_html_email(self, to_email, subject, html_content):
        if not self.api_key:
            print("  [Netcore] Error: NETCORE_API_KEY not found.")
            return {
                "success": False,
                "provider": "netcore",
                "message_id": None,
                "metadata": {"error": "API Key Missing"}
            }

        headers = {
            "api_key": self.api_key,
            "content-type": "application/json"
        }
        
        payload = {
            "from": {
                "email": self.from_email,
                "name": "Smarketer Pro"
            },
            "subject": subject,
            "content": [
                {
                    "type": "html",
                    "value": html_content
                }
            ],
            "personalizations": [
                {
                    "to": [{"email": to_email}]
                }
            ]
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            
            data = response.json()
            # Netcore Success: {"message": "Success", "data": {"message_id": "..."}}
            if data.get("message") == "Success":
                msg_id = data.get("data", {}).get("message_id")
                print(f"  [Netcore] Email sent to {to_email}")
                return {
                    "success": True,
                    "provider": "netcore",
                    "message_id": msg_id,
                    "metadata": {"status": "success"}
                }
            else:
                 print(f"  [Netcore] Error: {data}")
                 return {
                    "success": False,
                    "provider": "netcore",
                    "message_id": None,
                    "metadata": {"error": str(data)}
                }

        except Exception as e:
            print(f"  [Netcore] Failed to send to {to_email}: {e}")
            return {
                "success": False,
                "provider": "netcore",
                "message_id": None,
                "metadata": {"error": str(e)}
            }
