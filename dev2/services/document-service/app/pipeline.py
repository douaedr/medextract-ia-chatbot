"""Pipeline asynchrone : apres upload -> OCR -> IA (appels HTTP internes)."""
import httpx
from .config import settings

async def run_pipeline(document_id: str, file_path: str, mime_type: str):
    """Declenche l'OCR puis l'extraction IA en tache de fond.
    Chaque service met a jour le statut du document (OCR_DONE puis AI_DONE)."""
    async with httpx.AsyncClient(timeout=300) as client:
        # 1) OCR
        try:
            await client.post(
                f"{settings.OCR_SERVICE_URL}/api/ocr/process",
                json={"document_id": document_id, "file_path": file_path,
                      "mime_type": mime_type},
            )
        except Exception as e:
            print(f"[pipeline] OCR echoue pour {document_id}: {e}")
            return
        # 2) Extraction IA
        try:
            await client.post(
                f"{settings.AI_SERVICE_URL}/api/ai/extract",
                json={"document_id": document_id, "file_path": file_path},
            )
        except Exception as e:
            print(f"[pipeline] IA echoue pour {document_id}: {e}")
