import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ChatMessage
from ..schemas import ChatRequest, ChatResponse
from ..auth import get_current_user_id
from ..rag import knowledge_base, retriever, llm, safety

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.get("/health")
def health():
    return {"status": "ok", "service": "chatbot-service"}


@router.post("/message", response_model=ChatResponse)
async def send_message(req: ChatRequest,
                       db: Session = Depends(get_db),
                       user_id: str = Depends(get_current_user_id)):
    session_id = req.session_id or str(uuid.uuid4())

    # Enregistrer le message utilisateur
    db.add(ChatMessage(user_id=user_id, session_id=session_id,
                       role="user", content=req.message))
    db.commit()

    # --- Etape 5 (securite) : refus si demande de diagnostic ---
    if safety.is_diagnostic_request(req.message):
        answer = safety.refusal_answer()
    else:
        # Etape 1 : contexte patient
        patient_ctx, used_ctx = retriever.get_patient_context(db, user_id, req.message)
        # Etape 2 : base de connaissances
        knowledge = "\n".join(knowledge_base.search_knowledge(req.message))
        # Etapes 3-4 : prompt + LLM
        raw = await llm.ask_llm(patient_ctx, knowledge, req.message)
        # Etape 5-6 : filtrage + disclaimer
        answer = safety.ensure_disclaimer(safety.sanitize_output(raw))

    used_context = bool(retriever.get_patient_context(db, user_id)[1])

    # Enregistrer la reponse
    db.add(ChatMessage(user_id=user_id, session_id=session_id,
                       role="assistant", content=answer))
    db.commit()

    return ChatResponse(session_id=session_id, answer=answer,
                        used_context=used_context)


@router.get("/history")
def history(session_id: str = None, db: Session = Depends(get_db),
            user_id: str = Depends(get_current_user_id)):
    q = db.query(ChatMessage).filter(ChatMessage.user_id == user_id)
    if session_id:
        q = q.filter(ChatMessage.session_id == session_id)
    msgs = q.order_by(ChatMessage.created_at.asc()).all()
    return [{"session_id": str(m.session_id), "role": m.role,
             "content": m.content,
             "created_at": m.created_at.isoformat() if m.created_at else None}
            for m in msgs]


@router.delete("/history/{session_id}")
def clear_session(session_id: str, db: Session = Depends(get_db),
                  user_id: str = Depends(get_current_user_id)):
    deleted = (db.query(ChatMessage)
                 .filter(ChatMessage.user_id == user_id,
                         ChatMessage.session_id == session_id)
                 .delete())
    db.commit()
    return {"deleted": deleted, "session_id": session_id}
