
import requests
import json
import imaplib
import email
from email.header import decode_header
import time
from urllib.parse import urlencode

class CPanelManager:
    """
    Manages interactions with cPanel via UAPI for email creation and management.
    Also handles IMAP connections for verification.
    """
    def __init__(self, cpanel_url, cpanel_user, cpanel_token, use_password=True):
        self.cpanel_url = cpanel_url.rstrip('/')
        self.cpanel_user = cpanel_user
        self.cpanel_token = cpanel_token
        # If using password, we use Basic Auth. If using token, we use cpanel header.
        # Given the user context, we default to password (Basic Auth) or detection.
        self.use_password = use_password
        
        if not self.use_password:
             self.headers = {
                'Authorization': f'cpanel {cpanel_user}:{cpanel_token}'
            }
             self.auth = None
        else:
            self.headers = {}
            self.auth = (cpanel_user, cpanel_token)

    def _get_uapi_endpoint(self, module, function):
        return f"{self.cpanel_url}/execute/{module}/{function}"

    def create_email_account(self, email, password, quota=0):
        """
        Creates an email account via UAPI.
        Docs: https://api.docs.cpanel.net/openapi/cpanel/operation/add_pop/
        """
        # Parse user and domain from email
        if '@' not in email:
            raise ValueError("Invalid email format")
            
        user, domain = email.split('@')
        
        endpoint = self._get_uapi_endpoint("Email", "add_pop")
        params = {
            "email": user,
            "password": password,
            "quota": quota,
            "domain": domain
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, auth=self.auth)
            response.raise_for_status()
            result = response.json()
            
            if result.get("status") == 1:
                return {"status": "success", "data": result.get("data")}
            else:
                return {"status": "error", "message": result.get("errors", ["Unknown error"])[0]}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def list_email_accounts(self, domain=None):
        """Lists email accounts."""
        endpoint = self._get_uapi_endpoint("Email", "list_pops")
        params = {}
        if domain:
            params["domain"] = domain
            
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, auth=self.auth)
            result = response.json()
            if result.get("status") == 1:
                return result.get("data", [])
            return []
        except:
            return []

    def check_imap_for_verification(self, email_address, password, search_criteria="ALL", timeout=300):
        """
        Polls IMAP for a verification email.
        """
        # Assume standard cPanel IMAP port/host
        # Host is typically mail.domain.com or the cPanel IP
        # We try to derive it or use a configureable one.
        # For now, let's assume the cPanel URL's host is also the mail host, 
        # or we strip the protocol/port from cPanel URL.
        
        # Simple heuristic for hostname:
        from urllib.parse import urlparse
        parsed = urlparse(self.cpanel_url)
        imap_host = parsed.hostname
        
        # Poll logic
        start_time = time.time()
        
        try:
            mail = imaplib.IMAP4_SSL(imap_host)
            mail.login(email_address, password)
            mail.select("inbox")
            
            print(f"Polling IMAP for {email_address}...")
            
            while time.time() - start_time < timeout:
                status, messages = mail.search(None, search_criteria)
                if status == "OK" and messages[0]:
                    # Get the latest email
                    latest_email_id = messages[0].split()[-1]
                    status, data = mail.fetch(latest_email_id, "(RFC822)")
                    
                    raw_email = data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                        
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            if content_type == "text/plain" or content_type == "text/html":
                                try:
                                    body += part.get_payload(decode=True).decode()
                                except:
                                    pass
                    else:
                        body = msg.get_payload(decode=True).decode()
                        
                    mail.logout()
                    return {"subject": subject, "body": body}
                
                time.sleep(10)
                
            mail.logout()
            return None
            
        except Exception as e:
            print(f"IMAP Error: {e}")
            return None
