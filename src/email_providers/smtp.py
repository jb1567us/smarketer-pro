import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import get_smtp_config, config
from .base import EmailProvider

class SMTPProvider(EmailProvider):
    def __init__(self):
        host, port, user, password = get_smtp_config()
        self.smtp_server = host
        self.smtp_port = port
        self.username = user
        self.password = password
        self.from_email = user 
        
    def send_html_email(self, to_email, subject, html_content):
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
            print(f"  [SMTP] Email sent to {to_email}")
            return {
                "success": True,
                "provider": "smtp",
                "message_id": "smtp-sent",
                "metadata": {"host": self.smtp_server}
            }
        except Exception as e:
            print(f"  [SMTP] Failed to send to {to_email}: {e}")
            return {
                "success": False,
                "provider": "smtp",
                "message_id": None,
                "metadata": {"error": str(e)}
            }
