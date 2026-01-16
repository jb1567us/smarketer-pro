from abc import ABC, abstractmethod

class EmailProvider(ABC):
    @abstractmethod
    def send_html_email(self, to_email, subject, html_content):
        """
        Sends an HTML email. 
        Returns a dict: { "success": bool, "provider": str, "message_id": str, "metadata": dict }
        """
        pass
