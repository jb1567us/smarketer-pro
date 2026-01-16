from config import config
from .smtp import SMTPProvider
from .resend import ResendProvider
from .brevo import BrevoProvider
from .sendgrid import SendGridProvider
from .mailjet import MailjetProvider
from .mailgun import MailgunProvider
from .postmark import PostmarkProvider
from .mailersend import MailerSendProvider
from .sendpulse import SendPulseProvider
from .router import SmartEmailRouter

class EmailFactory:
    _instance = None

    @classmethod
    def get_provider(cls):
        if cls._instance:
            return cls._instance

        # Load from config
        provider_name = config.get('email', {}).get('provider', 'smtp')

        if provider_name == 'smart':
            cls._instance = SmartEmailRouter()
        elif provider_name == 'resend':
            cls._instance = ResendProvider()
        elif provider_name == 'brevo':
            cls._instance = BrevoProvider()
        elif provider_name == 'sendgrid':
            cls._instance = SendGridProvider()
        elif provider_name == 'mailjet':
            cls._instance = MailjetProvider()
        elif provider_name == 'mailgun':
            cls._instance = MailgunProvider()
        elif provider_name == 'postmark':
            cls._instance = PostmarkProvider()
        elif provider_name == 'mailersend':
            cls._instance = MailerSendProvider()
        elif provider_name == 'sendpulse':
            cls._instance = SendPulseProvider()
        else:
            cls._instance = SMTPProvider()
            
        return cls._instance
