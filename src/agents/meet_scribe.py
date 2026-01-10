from .base import BaseAgent
import json

class MeetScribeAgent(BaseAgent):
    """
    Agent inspired by 'MeetScribe' and 'Meeting Minute Writer' from LOLLMS.
    Specializes in analyzing meeting transcripts to extract actionable intelligence and drafting follow-ups.
    """
    def __init__(self, provider=None):
        super().__init__(
            role="Meeting Intelligence Officer",
            goal="Transform raw meeting notes or transcripts into structured minutes, action items, and follow-up emails.",
            provider=provider
        )

    def analyze_meeting_transcript(self, transcript_text):
        """
        Analyzes a meeting transcript to extract key information.
        """
        prompt = (
            "Analyze the following meeting transcript/notes.\n"
            "Extract:\n"
            "1. Key Decisions Made.\n"
            "2. Action Items (Who, What, By When).\n"
            "3. Open Questions/Issues.\n\n"
            "TRANSCRIPT:\n"
            f"'''{transcript_text}'''\n\n"
            "Return JSON with keys: 'decisions' (list), 'action_items' (list of objects with owner/task/deadline), 'open_issues' (list), 'brief_summary'."
        )
        return self.provider.generate_json(prompt)

    def generate_follow_up_email(self, transcript_text, recipients="All Attendees", tone="professional"):
        """
        Generates a follow-up email based on the meeting content.
        """
        prompt = (
            f"Draft a follow-up email for the meeting described in the transcript below.\n"
            f"Recipients: {recipients}\n"
            f"Tone: {tone}\n\n"
            "The email must:\n"
            "- Thank everyone for their time.\n"
            "- Summarize what was agreed upon.\n"
            "- clearly list the Action Items assigned to people.\n"
            "- propose next steps if any.\n\n"
            "TRANSCRIPT:\n"
            f"'''{transcript_text}'''\n\n"
            "Return JSON with keys: 'email_subject', 'email_body'."
        )
        return self.provider.generate_json(prompt)
