from .base import BaseAgent

class LinkedInAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="LinkedIn Outreach Specialist",
            goal="Draft high-converting LinkedIn InMail and connection requests based on profile highlights and intent signals.",
            provider=provider
        )

    def think(self, context):
        """
        Context should include:
        - Lead info (Name, Company, Bio)
        - LinkedIn profile highlights (from enrichment)
        - Intent signals
        """
        instructions = (
            "Draft a LinkedIn message for this lead.\n"
            "Rules:\n"
            "1. Maximum 300 characters for connection requests, 600 for InMail.\n"
            "2. Reference a specific professional achievement or intent signal (e.g. 'Congrats on the new launch').\n"
            "3. Sound like a peer, not a salesperson.\n"
            "4. Return both a 'Connection Request' and a 'Follow-up InMail'.\n\n"
            "Return JSON: {\n"
            "  'connection_request': str,\n"
            "  'inmail_body': str,\n"
            "  'personalization_strategy': str\n"
            "}"
        )
        return self.provider.generate_json(f"Lead Context:\n{context}\n\n{instructions}")

    def generate_comment(self, post_content):
        """
        Generates a thoughtful comment for a prospect's LinkedIn post.
        """
        instructions = (
            "Draft a thoughtful, value-add comment for this LinkedIn post.\n"
            "Avoid generic 'Great post!' or 'Thanks for sharing'.\n"
            "Ask a question or add a relevant insight.\n\n"
            "Post Content:\n" + post_content + "\n\n"
            "Return JSON: {'comment': str}"
        )
        return self.provider.generate_json(instructions)
