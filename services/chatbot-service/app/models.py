import uuid
from sqlalchemy import Column, String, Text, Float, Date, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from .database import Base

class Analysis(Base):
    __tablename__ = "analyses"
    id            = Column(UUID(as_uuid=True), primary_key=True)
    user_id       = Column(UUID(as_uuid=True))
    analysis_name = Column(String(255))
    value         = Column(Float)
    unit          = Column(String(50))
    ref_min       = Column(Float)
    ref_max       = Column(Float)
    status        = Column(String(20))
    analysis_date = Column(Date)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id    = Column(UUID(as_uuid=True), nullable=False)
    session_id = Column(UUID(as_uuid=True), nullable=False)
    role       = Column(String(20), nullable=False)
    content    = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
