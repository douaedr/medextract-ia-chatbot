from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class DocumentOut(BaseModel):
    id: UUID
    user_id: UUID
    filename: str
    original_name: str
    file_size: int
    mime_type: str
    doc_type: str
    status: str
    notes: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True

class DocumentDetail(DocumentOut):
    ocr_text: Optional[str] = None
