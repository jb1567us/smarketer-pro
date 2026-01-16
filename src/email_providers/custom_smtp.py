import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .base import EmailProvider

class CustomSMTPProvider(EmailProvider):
    def __init__(self, name, host, port, username, password):
        self.name = name
        self.smtp_server = host
        self.smtp_port = int(port)
        self.username = username
        self.password = password
        # We can't easily guess the 'from' email if not provided, 
        # so we rely on the caller to ensure 'from_email' in config matches or is allowed.
        # But for the Router, we usually pass 'from_email' from global config.

    def send_html_email(self, to_email, subject, html_content, from_email=None):
        # Allow overriding from_email if needed, otherwise use what's passed or default
        # The base.py signature is (self, to_email, subject, html_content). 
        # We might need to handle 'from_email' if the base class doesn't pass it. 
        # However, the current base/router design uses config['email']['from_email'].
        # We'll use the one from config inside the method if not stored.
        
        # NOTE: To make this robust, we should probably pass from_email to the init 
        # or fetch it from config here.
        from config import config
        sender = from_email or config['email'].get('from_email')
        
        if not self.username or not self.password or not self.smtp_server:
             return {
                "success": False,
                "provider": self.name,
                "message_id": None,
                "metadata": {"error": "Incomplete Credentials"}
            }

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = to_email

        part = MIMEText(html_content, "html")
        msg.attach(part)

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.sendmail(sender, to_email, msg.as_string())
            server.quit()
            
            print(f"  [{self.name}] Email sent to {to_email}")
            return {
                "success": True,
                "provider": self.name,
                "message_id": f"smtp-{self.name}-sent",
                "metadata": {"host": self.smtp_server}
            }
        except Exception as e:
            print(f"  [{self.name}] Failed to send to {to_email}: {e}")
            return {
                "success": False,
                "provider": self.name,
                "message_id": None,
                "metadata": {"error": str(e)}
            }
