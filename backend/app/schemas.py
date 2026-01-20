# backend/app/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class InteractionType(str, Enum):
    MEETING = "Meeting" 
    CALL = "Call"
    EMAIL = "Email"
    VIRTUAL = "Virtual"

class OutcomeType(str, Enum):
    POSITIVE = "Positive"
    NEUTRAL = "Neutral"
    NEGATIVE = "Negative"


class InteractionBase(BaseModel):
    hcp_name: str
    attendees: Optional[str] = None
    date: datetime
    time: Optional[str] = None
    interaction_type: InteractionType
    topics: Optional[str] = None
    attachments: Optional[str] = None
    materials_distributed: Optional[str] = None
    outcomes: Optional[OutcomeType] = None
    follow_up: Optional[str] = None
    summary: Optional[str] = None

class InteractionCreate(InteractionBase):
    pass  # For creating new

class InteractionUpdate(BaseModel):
    hcp_name: Optional[str] = None
    attendees: Optional[str] = None
    date: Optional[datetime] = None
    time: Optional[str] = None
    interaction_type: Optional[InteractionType] = None
    topics: Optional[str] = None
    attachments: Optional[str] = None
    materials_distributed: Optional[str] = None
    outcomes: Optional[OutcomeType] = None
    follow_up: Optional[str] = None
    summary: Optional[str] = None

class Interaction(InteractionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Allows ORM mode (SQLAlchemy → Pydantic)