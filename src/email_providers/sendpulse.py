import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import config
from .base import EmailProvider

class SendPulseProvider(EmailProvider):
    def __init__(self):
        # SendPulse is easiest configured via SMTP for casual use
        # Host: smtp-pulse.com, Port: 2525 or 587
        self.smtp_server = "smtp-pulse.com"
        self.smtp_port = 587
        self.username = os.getenv("SENDPULSE_EMAIL") or config['email'].get('from_email') # Often the login email
        self.password = os.getenv("SENDPULSE_SMTP_PASSWORD") # From SMTP settings in SendPulse
        self.from_email = config['email'].get('from_email')

    def send_html_email(self, to_email, subject, html_content):
        if not self.username or not self.password:
             print("  [SendPulse] Error: SENDPULSE_EMAIL or SENDPULSE_SMTP_PASSWORD not found.")
             return {
                "success": False,
                "provider": "sendpulse",
                "message_id": None,
                "metadata": {"error": "Credentials Missing"}
            }

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.from_email
        msg["To"] = to_email

        part = MIMEText(html_content, "html")
        msg.attach(part)

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.from_email, to_email, msg.as_string())
            server.quit()
            
            print(f"  [SendPulse] Email sent to {to_email}")
            return {
                "success": True,
                "provider": "sendpulse",
                "message_id": "smtp-pulse-sent",
                "metadata": {"status": "sent"}
            }
        except Exception as e:
            print(f"  [SendPulse] Failed to send to {to_email}: {e}")
            return {
                "success": False,
                "provider": "sendpulse",
                "message_id": None,
                "metadata": {"error": str(e)}
            }
