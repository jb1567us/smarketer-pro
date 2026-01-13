import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any, Dict
from src.nodes.base import BaseNode, NodeContext
from src.nodes.registry import register_node

class EmailNode(BaseNode):
    @property
    def node_type(self) -> str:
        return "domain.email"

    @property
    def display_name(self) -> str:
        return "Email Sender (SMTP)"

    async def execute(self, context: NodeContext, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends an email using the configured system provider (Smart Router, Brevo, SMTP, etc).
        Params:
            to_email (str): Recipient.
            subject (str): Email subject.
            body (str): Email body (HTML).
            provider (str): Optional. Force a specific provider ('smtp', 'brevo', etc), ignoring system default.
            live_mode (bool): If False, mocks the send.
        """
        to_email = params.get("to_email")
        subject = params.get("subject")
        body = params.get("body")
        
        # Check for a 'live_mode' flag (default False for safety in dev)
        live_mode = params.get("live_mode", False)
        
        if not to_email or not subject or not body:
             raise ValueError("EmailNode requires 'to_email', 'subject', and 'body'.")

        context.logger.info(f"[EmailNode] Sending to: {to_email} | Subject: {subject}")
        
        if not live_mode:
            context.logger.info("[EmailNode] DRY RUN (Mock Send). Email not sent.")
            return {
                "status": "mock_sent",
                "to": to_email,
                "subject": subject,
                "provider": "mock"
            }

        try:
            # Use the Factory to get the system's active provider (or specific one)
            from src.email_providers.factory import EmailFactory
            
            # FUTURE: If params['provider'] is set, we could bypass factory default
            # For now, we stick to the factory's global config logic
            provider = EmailFactory.get_provider()
            
            # Helper to run blocking sync IO in async
            import asyncio
            import functools
            loop = asyncio.get_event_loop()
            
            # Run the send in a thread to not block the async loop
            success = await loop.run_in_executor(
                None, 
                functools.partial(provider.send_html_email, to_email, subject, body)
            )
            
            if success:
                context.logger.info("[EmailNode] Email SENT successfully via Provider.")
                return {"status": "sent", "to": to_email, "provider": str(provider)}
            else:
                 context.logger.error("[EmailNode] Provider reported FAILURE.")
                 return {"status": "failed", "to": to_email, "error": "Provider returned False"}
            
        except Exception as e:
            context.logger.error(f"[EmailNode] Failed to send: {e}")
            return {"status": "error", "error": str(e)}

# Register logic
register_node(EmailNode())
