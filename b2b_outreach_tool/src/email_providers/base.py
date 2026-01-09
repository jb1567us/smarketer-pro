from abc import ABC, abstractmethod

class EmailProvider(ABC):
    @abstractmethod
    def send_html_email(self, to_email, subject, html_content):
        """Sends an HTML email. Returns True on success, False on failure."""
        pass
