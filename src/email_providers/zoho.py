import os
import requests
from config import config
from .base import EmailProvider

class ZohoProvider(EmailProvider):
    def __init__(self):
        # ZeptoMail uses a Send Mail Token
        self.api_token = os.getenv("ZOHO_ZEPTOMAIL_TOKEN")
        self.from_email = config['email'].get('from_email')
        self.api_url = "https://api.zeptomail.com/v1.1/email"

    def send_html_email(self, to_email, subject, html_content):
        if not self.api_token:
            print("  [Zoho] Error: ZOHO_ZEPTOMAIL_TOKEN not found.")
            return {
                "success": False,
                "provider": "zoho",
                "message_id": None,
                "metadata": {"error": "Token Missing"}
            }

        headers = {
            "Authorization": self.api_token, # Scheme is often directly the token or "Zoho-enczapikey <token>" depending on generation. Assuming standard Authorization header use.
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # NOTE: ZeptoMail sometimes requires the token format: "Zoho-enczapikey wSsVR6Ms..."
        # If the user pastes the full key including prefix, it works. If not, we might need to prepend.
        # For now, we assume the user pastes the full Authorization header value provided by ZeptoMail.
        
        payload = {
            "from": {
                "address": self.from_email,
                "name": "Smarketer Pro" 
            },
            "to": [
                {
                    "email_address": {
                        "address": to_email,
                    }
                }
            ],
            "subject": subject,
            "htmlbody": html_content
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            
            if response.status_code in [200, 201]:
                data = response.json()
                # ZeptoMail structure: { data: [ { code, additional_info, message } ], message, request_id }
                # It's a batch API, so we check the first item
                if data.get("data"):
                    item = data["data"][0]
                    print(f"  [Zoho] Email sent to {to_email}")
                    return {
                        "success": True,
                        "provider": "zoho",
                        "message_id": data.get("request_id"), # Or specific message ID if available
                        "metadata": {"status": item.get("message")}
                    }
                else:
                     print(f"  [Zoho] Unexpected response: {data}")
                     return {
                        "success": True, # Assume queued?
                        "provider": "zoho",
                        "message_id": data.get("request_id"),
                        "metadata": {"info": "No data block"}
                    }
            else:
                 print(f"  [Zoho] Error: {response.text}")
                 return {
                    "success": False,
                    "provider": "zoho",
                    "message_id": None,
                    "metadata": {"error": response.text, "status": response.status_code}
                }

        except Exception as e:
            print(f"  [Zoho] Failed to send to {to_email}: {e}")
            return {
                "success": False,
                "provider": "zoho",
                "message_id": None,
                "metadata": {"error": str(e)}
            }
