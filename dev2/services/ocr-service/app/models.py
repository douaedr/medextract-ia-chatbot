import uuid
from sqlalchemy import (Column, String, Text, Integer, Float, DateTime,
                        ForeignKey, func)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from .database import Base

class Document(Base):
    """Vue partielle de la table documents (pour lire file_path / maj status)."""
    __tablename__ = "documents"
    id        = Column(UUID(as_uuid=True), primary_key=True)
    file_path = Column(Text)
    mime_type = Column(String(100))
    status    = Column(String(20))
    ocr_text  = Column(Text)

class OCRResult(Base):
    __tablename__ = "ocr_results"
    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id     = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    raw_text        = Column(Text)
    words           = Column(JSONB)     # [{word, confidence, bbox, page}]
    page_count      = Column(Integer, default=1)
    ocr_engine      = Column(String(50), default="PaddleOCR")
    processing_time = Column(Float)
    created_at      = Column(DateTime, server_default=func.now())
