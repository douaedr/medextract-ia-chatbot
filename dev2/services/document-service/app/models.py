import uuid
from sqlalchemy import Column, String, Text, BigInteger, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from .database import Base

class Document(Base):
    __tablename__ = "documents"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id       = Column(UUID(as_uuid=True), nullable=False)
    filename      = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_path     = Column(Text, nullable=False)
    file_size     = Column(BigInteger, nullable=False)
    mime_type     = Column(String(100), nullable=False)
    doc_type      = Column(String(20), default="UNKNOWN")
    status        = Column(String(20), default="PENDING")
    ocr_text      = Column(Text, nullable=True)
    notes         = Column(Text, nullable=True)
    created_at    = Column(DateTime, server_default=func.now())
