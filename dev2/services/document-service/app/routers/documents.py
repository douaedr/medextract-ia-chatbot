import os
import uuid
import shutil
from fastapi import (APIRouter, Depends, HTTPException, UploadFile, File,
                     Form, BackgroundTasks)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..config import settings
from ..models import Document
from ..schemas import DocumentOut, DocumentDetail
from ..auth import get_current_user, CurrentUser
from ..pipeline import run_pipeline

router = APIRouter(prefix="/api/documents", tags=["documents"])

ALLOWED_MIME = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
}


@router.post("/upload", response_model=DocumentOut, status_code=201)
async def upload(background: BackgroundTasks,
                 file: UploadFile = File(...),
                 notes: str = Form(None),
                 doc_type: str = Form("UNKNOWN"),
                 db: Session = Depends(get_db),
                 current: CurrentUser = Depends(get_current_user)):
    # --- Validation du type ---
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(400, "Type de fichier non supporte (PDF, JPG, PNG uniquement)")

    # --- Lecture + validation de la taille ---
    content = await file.read()
    size = len(content)
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if size > max_bytes:
        raise HTTPException(400, f"Fichier trop grand (max {settings.MAX_UPLOAD_MB} MB)")
    if size == 0:
        raise HTTPException(400, "Fichier vide")

    # --- Stockage physique /app/uploads/{user_id}/ ---
    user_dir = os.path.join(settings.UPLOAD_DIR, str(current.id))
    os.makedirs(user_dir, exist_ok=True)
    ext = ALLOWED_MIME[file.content_type]
    stored_name = f"{uuid.uuid4()}{ext}"
    dest = os.path.join(user_dir, stored_name)
    with open(dest, "wb") as f:
        f.write(content)

    # --- Type affiche : garde le type metier fourni, sinon deduit du format ---
    SEMANTIC = {"BLOOD_TEST", "RADIOLOGY", "PRESCRIPTION", "REPORT"}
    if doc_type in SEMANTIC:
        final_type = doc_type
    else:
        final_type = "PDF" if file.content_type == "application/pdf" else "IMAGE"

    # --- Enregistrement en base ---
    doc = Document(
        user_id=current.id,
        filename=stored_name,
        original_name=file.filename,
        file_path=dest,
        file_size=size,
        mime_type=file.content_type,
        doc_type=final_type,
        status="PENDING",
        notes=notes,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # --- Declenchement du pipeline OCR -> IA en arriere-plan ---
    background.add_task(run_pipeline, str(doc.id), dest, file.content_type)
    return doc


@router.get("/health")
def health():
    return {"status": "ok", "service": "document-service"}


@router.get("/", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db),
                   current: CurrentUser = Depends(get_current_user)):
    return (db.query(Document)
              .filter(Document.user_id == current.id)
              .order_by(Document.created_at.desc())
              .all())


def _get_owned(document_id: str, db: Session, current: CurrentUser) -> Document:
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc or str(doc.user_id) != str(current.id):
        raise HTTPException(404, "Document introuvable")
    return doc


@router.get("/{document_id}", response_model=DocumentDetail)
def get_document(document_id: str, db: Session = Depends(get_db),
                 current: CurrentUser = Depends(get_current_user)):
    return _get_owned(document_id, db, current)


@router.delete("/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db),
                    current: CurrentUser = Depends(get_current_user)):
    doc = _get_owned(document_id, db, current)
    try:
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
    except OSError:
        pass
    db.delete(doc)
    db.commit()
    return {"message": "Document supprime"}


@router.get("/{document_id}/download")
def download(document_id: str, db: Session = Depends(get_db),
             current: CurrentUser = Depends(get_current_user)):
    doc = _get_owned(document_id, db, current)
    if not os.path.exists(doc.file_path):
        raise HTTPException(404, "Fichier introuvable sur le disque")
    return FileResponse(doc.file_path, media_type=doc.mime_type,
                        filename=doc.original_name)
