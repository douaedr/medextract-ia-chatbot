import uuid
from sqlalchemy import Column, String, Float, Date, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from .database import Base

class Document(Base):
    __tablename__ = "documents"
    id         = Column(UUID(as_uuid=True), primary_key=True)
    user_id    = Column(UUID(as_uuid=True))
    doc_type   = Column(String(20))
    status     = Column(String(20))
    created_at = Column(DateTime)

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
    created_at    = Column(DateTime)
