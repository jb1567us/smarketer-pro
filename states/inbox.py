import reflex as rx
from .base import BaseState, DB_AVAILABLE
from ..models import ChatSession, Message

class InboxState(BaseState):
    """Inbox and Messaging state."""
    inbox_sessions: list[ChatSession] = []
    inbox_messages: list[Message] = []
    selected_session_id: int = 0
    new_message_content: str = ""
    is_sending_message: bool = False

    async def load_inbox(self):
        """Load chat sessions for inbox."""
        if DB_AVAILABLE:
            try:
                from backend.database import get_chat_sessions, get_chat_history
                raw_sessions = get_chat_sessions()
                async with self:
                    self.inbox_sessions = [ChatSession(**s) for s in raw_sessions]
                    if self.inbox_sessions and not self.selected_session_id:
                        self.selected_session_id = self.inbox_sessions[0].id
                        raw_messages = get_chat_history(self.selected_session_id)
                        self.inbox_messages = [Message(**m) for m in raw_messages]
            except Exception as e:
                print(f"Error loading inbox: {e}")

    async def select_inbox_session(self, session_id: int):
        """Select and load a chat session."""
        self.selected_session_id = session_id
        if DB_AVAILABLE:
            from backend.db.chat import get_chat_history
            raw_messages = get_chat_history(session_id)
            self.inbox_messages = [Message(**m) for m in raw_messages]
    async def send_inbox_message(self):
        """Send a message in the selected inbox session."""
        if not self.new_message_content or not self.selected_session_id:
            return
        
        content = self.new_message_content
        self.new_message_content = ""
        self.is_sending_message = True
        yield
        
        if DB_AVAILABLE:
            try:
                from backend.database import add_message
                add_message(self.selected_session_id, "user", content)
                self.add_log(f"Sent message to session {self.selected_session_id}")
                
                # Simulate AI response
                await asyncio.sleep(1)
                add_message(self.selected_session_id, "AI", f"Received your message: {content[:20]}...")
                
                await self.select_inbox_session(self.selected_session_id)
            except Exception as e:
                self.add_log(f"Error sending message: {e}")
        else:
            self.inbox_messages.append(Message(role="user", content=content))
            await asyncio.sleep(0.5)
            self.inbox_messages.append(Message(role="AI", content="This is a prototype response."))
            
        self.is_sending_message = False
