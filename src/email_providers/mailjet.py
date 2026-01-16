import os
import requests
import base64
from config import config
from .base import EmailProvider

class MailjetProvider(EmailProvider):
    def __init__(self):
        self.api_key = os.getenv("MAILJET_API_KEY")
        self.secret_key = os.getenv("MAILJET_SECRET_KEY")
        self.from_email = config['email'].get('from_email')
        self.api_url = "https://api.mailjet.com/v3.1/send"

    def send_html_email(self, to_email, subject, html_content):
        if not self.api_key or not self.secret_key:
            print("  [Mailjet] Error: MAILJET_API_KEY or MAILJET_SECRET_KEY not found.")
            return {
                "success": False,
                "provider": "mailjet",
                "message_id": None,
                "metadata": {"error": "Credentials Missing"}
            }

        headers = {
            "Content-Type": "application/json"
        }
        
        # Mailjet V3.1 format
        payload = {
            "Messages": [
                {
                    "From": {
                        "Email": self.from_email,
                        "Name": "Smarketer Pro"
                    },
                    "To": [
                        {
                            "Email": to_email
                        }
                    ],
                    "Subject": subject,
                    "HTMLPart": html_content
                }
            ]
        }

        try:
            # Mailjet uses Basic Auth
            response = requests.post(
                self.api_url, 
                auth=(self.api_key, self.secret_key), 
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            # Check for specific message status
            messages = data.get("Messages", [])
            if not messages:
                 return {
                    "success": False,
                    "provider": "mailjet",
                    "message_id": None,
                    "metadata": {"error": "No message response"}
                }
            
            msg = messages[0]
            if msg.get("Status") == "success":
                msg_id = msg.get("To", [{}])[0].get("MessageID")
                print(f"  [Mailjet] Email sent to {to_email} (ID: {msg_id})")
                return {
                    "success": True,
                    "provider": "mailjet",
                    "message_id": str(msg_id),
                    "metadata": {"status": "success"}
                }
            else:
                 print(f"  [Mailjet] Error: {msg}")
                 return {
                    "success": False,
                    "provider": "mailjet",
                    "message_id": None,
                    "metadata": {"error": str(msg)}
                }

        except Exception as e:
            print(f"  [Mailjet] Failed to send to {to_email}: {e}")
            return {
                "success": False,
                "provider": "mailjet",
                "message_id": None,
                "metadata": {"error": str(e)}
            }
