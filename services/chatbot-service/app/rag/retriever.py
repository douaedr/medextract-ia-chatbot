"""Etape 1 du RAG : recuperer les analyses du patient (contexte personnel)."""
from sqlalchemy.orm import Session
from ..models import Analysis

def get_patient_context(db: Session, user_id: str, query: str = "") -> tuple[str, bool]:
    analyses = (db.query(Analysis)
                  .filter(Analysis.user_id == user_id)
                  .order_by(Analysis.analysis_date.desc().nullslast())
                  .limit(30).all())
    if not analyses:
        return "", False

    lines = []
    for a in analyses:
        ref = ""
        if a.ref_min is not None and a.ref_max is not None:
            ref = f" (normes {a.ref_min}-{a.ref_max})"
        date = f" le {a.analysis_date}" if a.analysis_date else ""
        lines.append(f"- {a.analysis_name} : {a.value} {a.unit or ''}"
                     f" [{a.status}]{ref}{date}")
    return "\n".join(lines), True
