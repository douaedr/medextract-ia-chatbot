import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..config import settings
from ..models import Document, OCRResult, MedicalResult, Analysis
from ..schemas import ExtractRequest
from ..auth import get_current_user_id
from ..extraction import regex_extractor, layoutlm_extractor

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.get("/health")
def health():
    return {"status": "ok", "service": "ai-service"}


@router.get("/model-info")
def model_info():
    loaded = layoutlm_extractor.is_loaded()
    return {
        "model_loaded": loaded,
        "model_version": "layoutlmv3-medical" if loaded else "regex-v1",
        "fallback": "regex" if not loaded else None,
        "labels": layoutlm_extractor.LABELS,
    }


@router.post("/extract")
def extract(req: ExtractRequest, db: Session = Depends(get_db)):
    """Appele par le Document Service apres l'OCR (pas d'auth : interne)."""
    doc = db.query(Document).filter(Document.id == req.document_id).first()
    if not doc:
        raise HTTPException(404, "Document introuvable")

    ocr = db.query(OCRResult).filter(OCRResult.document_id == req.document_id).first()
    if not ocr or not ocr.raw_text:
        raise HTTPException(400, "OCR non disponible pour ce document")

    start = time.time()

    # --- Choix du moteur : LayoutLMv3 si charge, sinon regles regex ---
    result = None
    if layoutlm_extractor.is_loaded() and ocr.words:
        try:
            from PIL import Image
            image = Image.open(doc.file_path).convert("RGB") if doc.file_path else None
            if image is not None:
                page0 = [w for w in ocr.words if w.get("page", 0) == 0]
                result = layoutlm_extractor.extract_with_model(page0, image)
        except Exception as e:
            print(f"[ai] LayoutLMv3 echoue, repli regex : {e}")

    if result is None:
        result = regex_extractor.extract_from_text(ocr.raw_text)

    # --- Sauvegarde : on remplace tout resultat precedent ---
    db.query(MedicalResult).filter(MedicalResult.document_id == req.document_id).delete()

    mr = MedicalResult(
        document_id=req.document_id,
        user_id=doc.user_id,
        doc_type=doc.doc_type or "UNKNOWN",
        patient_name=result.get("patient_name"),
        doctor_name=result.get("doctor_name"),
        lab_name=result.get("lab_name"),
        model_version=result.get("model_version"),
        processing_time=round(time.time() - start, 3),
    )
    db.add(mr)
    db.flush()   # obtenir mr.id

    for a in result.get("analyses", []):
        db.add(Analysis(
            medical_result_id=mr.id,
            user_id=doc.user_id,
            analysis_name=a["analysis_name"],
            value=a["value"],
            unit=a["unit"],
            ref_min=a["ref_min"],
            ref_max=a["ref_max"],
            status=a["status"],
            confidence=a["confidence"],
            bbox=a.get("bbox"),
            analysis_date=a.get("analysis_date"),
        ))

    doc.status = "AI_DONE"
    db.commit()

    return {
        "document_id": req.document_id,
        "status": "AI_DONE",
        "model_version": mr.model_version,
        "analyses_count": len(result.get("analyses", [])),
        "processing_time": mr.processing_time,
    }


@router.get("/results/{document_id}")
def get_results(document_id: str, db: Session = Depends(get_db),
                user_id: str = Depends(get_current_user_id)):
    mr = db.query(MedicalResult).filter(MedicalResult.document_id == document_id).first()
    if not mr or str(mr.user_id) != str(user_id):
        raise HTTPException(404, "Aucun resultat pour ce document")
    analyses = db.query(Analysis).filter(Analysis.medical_result_id == mr.id).all()
    return {
        "document_id": str(mr.document_id),
        "patient_name": mr.patient_name,
        "doctor_name": mr.doctor_name,
        "lab_name": mr.lab_name,
        "doc_type": mr.doc_type,
        "model_version": mr.model_version,
        "processing_time": mr.processing_time,
        "analyses": [{
            "analysis_name": a.analysis_name, "value": a.value, "unit": a.unit,
            "ref_min": a.ref_min, "ref_max": a.ref_max, "status": a.status,
            "confidence": a.confidence, "bbox": a.bbox,
            "analysis_date": a.analysis_date.isoformat() if a.analysis_date else None,
        } for a in analyses],
    }


@router.get("/history/{user_id}")
def get_history(user_id: str, db: Session = Depends(get_db),
                current_user_id: str = Depends(get_current_user_id)):
    if str(user_id) != str(current_user_id):
        raise HTTPException(403, "Acces refuse")
    results = (db.query(MedicalResult)
                 .filter(MedicalResult.user_id == user_id)
                 .order_by(MedicalResult.created_at.desc())
                 .all())
    return [{
        "document_id": str(r.document_id),
        "doc_type": r.doc_type,
        "model_version": r.model_version,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    } for r in results]
