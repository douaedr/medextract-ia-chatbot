import uuid
from sqlalchemy import (Column, String, Text, Float, Date, DateTime,
                        ForeignKey, func)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from .database import Base

class Document(Base):
    __tablename__ = "documents"
    id        = Column(UUID(as_uuid=True), primary_key=True)
    user_id   = Column(UUID(as_uuid=True))
    file_path = Column(Text)
    doc_type  = Column(String(20))
    status    = Column(String(20))
    ocr_text  = Column(Text)

class OCRResult(Base):
    __tablename__ = "ocr_results"
    id          = Column(UUID(as_uuid=True), primary_key=True)
    document_id = Column(UUID(as_uuid=True))
    raw_text    = Column(Text)
    words       = Column(JSONB)

class MedicalResult(Base):
    __tablename__ = "medical_results"
    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id     = Column(UUID(as_uuid=True), ForeignKey("documents.id"))
    user_id         = Column(UUID(as_uuid=True))
    doc_type        = Column(String(20))
    patient_name    = Column(String(255))
    doctor_name     = Column(String(255))
    lab_name        = Column(String(255))
    model_version   = Column(String(100))
    processing_time = Column(Float)
    created_at      = Column(DateTime, server_default=func.now())

class Analysis(Base):
    __tablename__ = "analyses"
    id                = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    medical_result_id = Column(UUID(as_uuid=True), ForeignKey("medical_results.id"))
    user_id           = Column(UUID(as_uuid=True))
    analysis_name     = Column(String(255))
    value             = Column(Float)
    unit              = Column(String(50))
    ref_min           = Column(Float)
    ref_max           = Column(Float)
    status            = Column(String(20), default="UNKNOWN")
    confidence        = Column(Float)
    bbox              = Column(JSONB)
    analysis_date     = Column(Date)
    created_at        = Column(DateTime, server_default=func.now())
