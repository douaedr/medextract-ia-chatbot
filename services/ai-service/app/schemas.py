from typing import Optional
from pydantic import BaseModel

class ExtractRequest(BaseModel):
    document_id: str
    file_path: Optional[str] = None
