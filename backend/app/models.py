# backend/app/models.py
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from sqlalchemy.sql import func
from .database import Base
import enum
from datetime import datetime

class InteractionType(enum.Enum):
    MEETING = "Meeting"
    CALL = "Call"
    EMAIL = "Email"
    VIRTUAL = "Virtual"

class OutcomeType(enum.Enum):
    POSITIVE = "Positive"
    NEUTRAL = "Neutral"
    NEGATIVE = "Negative"

class Interaction(Base):
    __tablename__ = "hcp_interactions"  # table name in DB

    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String(255), index=True, nullable=False)
    attendees = Column(Text) # e.g. "Dr. Smith, Dr. Jones"
    date = Column(DateTime, nullable=False)
    time = Column(String(50))  # e.g. "14:30"
    interaction_type = Column(Enum(InteractionType), nullable=False)
    topics = Column(Text)  # e.g. "Product X efficacy, side effects"
    attachments = Column(Text)  # comma-separated or JSON string
    materials_distributed = Column(Text)
    outcomes = Column(Enum(OutcomeType))
    follow_up = Column(Text)  # e.g. "Send samples next week"
    summary = Column(Text)  # LLM-generated summary
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())