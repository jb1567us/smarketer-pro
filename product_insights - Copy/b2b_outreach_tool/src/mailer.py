import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import os
import random

class Mailer:
    def __init__(self, smtp_server, smtp_port, username, password, from_email):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.daily_limit = 100 # Safe limit for free Gmail/Outlook
        self.sent_count = 0

    def connect(self):
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            return server
        except Exception as e:
            print(f"SMTP Connection Error: {e}")
            return None

    def send_email(self, to_email, subject, html_content):
        if self.sent_count >= self.daily_limit:
            print("Daily limit reached for this account.")
            return False

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.from_email
        msg["To"] = to_email

        part = MIMEText(html_content, "html")
        msg.attach(part)

        try:
            server = self.connect()
            if server:
                server.sendmail(self.from_email, to_email, msg.as_string())
                server.quit()
                self.sent_count += 1
                print(f"Email sent to {to_email}")
                return True
        except Exception as e:
            print(f"Failed to send to {to_email}: {e}")
        
        return False

# Example Template
def get_article_template(business_name=""):
    # This is a placeholder. 
    # Realistically, this would be more sophisticated with actual links.
    return f"""
    <html>
      <body>
        <p>Hi team at {business_name or 'contact'},</p>
        <p>I found your business while researching industry leaders and wanted to share an article that I think you'll find valuable.</p>
        <p><strong><a href="https://example.com/article">How Product Insights Can Transform Your Workflow</a></strong></p>
        <p>Our SaaS app solves key pain points in B2B data analysis. I'd love to hear your thoughts.</p>
        <p>Best,<br>The Product Insights Team</p>
        <p style="font-size: small; color: gray;">
          <a href="#">Unsubscribe</a> | 123 Business Rd, City, Country
        </p>
      </body>
    </html>
    """

if __name__ == "__main__":
    # Test (requires env vars)
    user = os.getenv("SMTP_USER")
    pw = os.getenv("SMTP_PASS")
    if user and pw:
        mailer = Mailer("smtp.gmail.com", 587, user, pw, user)
        # mailer.send_email("test@example.com", "Test Subject", get_article_template())
    else:
        print("Set SMTP_USER and SMTP_PASS to test mailer.")
