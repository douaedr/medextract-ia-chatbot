from typing import Optional
from pydantic import BaseModel

class OCRProcessRequest(BaseModel):
    document_id: str
    file_path: Optional[str] = None    # optionnel : sinon lu depuis la BDD
    mime_type: Optional[str] = None

class WordBox(BaseModel):
    word: str
    confidence: float
    bbox: list[int]     # [x1, y1, x2, y2]
    page: int

class OCRResultOut(BaseModel):
    document_id: str
    raw_text: str
    words: list[WordBox]
    page_count: int
    ocr_engine: str
    processing_time: float
