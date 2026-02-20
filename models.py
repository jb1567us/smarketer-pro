from pydantic import BaseModel
from typing import Optional

class Message(BaseModel):
    role: str
    content: str
    
class ChatSession(BaseModel):
    id: int
    title: str
    
class Lead(BaseModel):
    id: int
    email: str | None = None
    company_name: str | None = None
    source: str | None = None
    status: str | None = "new"
    url: str | None = None
    contact_person: str | None = None
    tech_stack: str | None = None
    created_at: int | None = None
    category: str | None = None
    industry: str | None = None
    confidence: float | None = 0.0
    notes: str | None = None
    intent_signals: str | None = None

class Campaign(BaseModel):
    id: int
    name: str | None = None
    niche: str | None = None
    status: str | None = "draft"
