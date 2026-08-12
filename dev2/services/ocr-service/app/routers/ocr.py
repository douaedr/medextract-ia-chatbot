from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Document, OCRResult
from ..schemas import OCRProcessRequest
from ..ocr_engine import run_ocr

router = APIRouter(prefix="/api/ocr", tags=["ocr"])


@router.get("/health")
def health():
    return {"status": "ok", "service": "ocr-service"}


@router.post("/process")
def process(req: OCRProcessRequest, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == req.document_id).first()
    if not doc:
        raise HTTPException(404, "Document introuvable")

    file_path = req.file_path or doc.file_path
    mime_type = req.mime_type or doc.mime_type

    try:
        result = run_ocr(file_path, mime_type)
    except Exception as e:
        doc.status = "ERROR"
        db.commit()
        raise HTTPException(500, f"Echec OCR : {e}")

    # Un seul resultat OCR par document : on remplace l'ancien.
    db.query(OCRResult).filter(OCRResult.document_id == req.document_id).delete()
    ocr = OCRResult(
        document_id=req.document_id,
        raw_text=result["raw_text"],
        words=result["words"],
        page_count=result["page_count"],
        ocr_engine="PaddleOCR",
        processing_time=result["processing_time"],
    )
    db.add(ocr)

    # Mise a jour du document
    doc.ocr_text = result["raw_text"]
    doc.status = "OCR_DONE"
    db.commit()

    return {
        "document_id": req.document_id,
        "status": "OCR_DONE",
        "page_count": result["page_count"],
        "word_count": len(result["words"]),
        "processing_time": result["processing_time"],
    }


@router.get("/{document_id}")
def get_result(document_id: str, db: Session = Depends(get_db)):
    ocr = db.query(OCRResult).filter(OCRResult.document_id == document_id).first()
    if not ocr:
        raise HTTPException(404, "Aucun resultat OCR pour ce document")
    return {
        "document_id": str(ocr.document_id),
        "raw_text": ocr.raw_text,
        "words": ocr.words,
        "page_count": ocr.page_count,
        "ocr_engine": ocr.ocr_engine,
        "processing_time": ocr.processing_time,
    }
