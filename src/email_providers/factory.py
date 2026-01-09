from config import config
from .smtp import SMTPProvider
from .resend import ResendProvider
from .brevo import BrevoProvider
from .sendgrid import SendGridProvider
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
        else:
            cls._instance = SMTPProvider()
            
        return cls._instance
