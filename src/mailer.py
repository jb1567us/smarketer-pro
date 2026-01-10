from config import config
from email_providers import EmailFactory

class Mailer:
    def __init__(self):
        self.daily_limit = config["email"]["daily_limit"]
        self.sent_count = 0
        self.provider = EmailFactory.get_provider()

    def send_email(self, to_email, subject, html_content):
        if self.sent_count >= self.daily_limit:
            print("Daily limit reached for this account.")
            return False

        success = self.provider.send_html_email(to_email, subject, html_content)
        if success:
            self.sent_count += 1
        return success

def get_email_content(business_name=""):
    # In a real scenario, we'd load the HTML template from the file specified in config
    # template_path = config["email"]["template_file"]
    # For now, we use the subject from config and a dynamic body
    subject = config["email"]["subject"]
    
    body = f"""
    <html>
      <body>
        <p>Hi team at {business_name or 'contact'},</p>
        <p>I found your business while researching industry leaders and wanted to share an article that I think you'll find valuable.</p>
        <p><strong><a href="https://example.com/article">{subject}</a></strong></p>
        <p>Our SaaS app solves key pain points in B2B data analysis. I'd love to hear your thoughts.</p>
        <p>Best,<br>The Product Insights Team</p>
        <p style="font-size: small; color: gray;">
           123 Business Rd, City, Country
        </p>
      </body>
    </html>
    """
    return subject, body

if __name__ == "__main__":
    # Test (requires env vars)
    user = os.getenv("SMTP_USER")
    pw = os.getenv("SMTP_PASS")
    if user and pw:
        mailer = Mailer("smtp.gmail.com", 587, user, pw, user)
        # mailer.send_email("test@example.com", "Test Subject", get_article_template())
    else:
        print("Set SMTP_USER and SMTP_PASS to test mailer.")
