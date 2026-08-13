from collections import defaultdict
from statistics import mean
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Document, Analysis
from ..auth import get_current_user_id
from ..excel_export import build_excel

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/health")
def health():
    return {"status": "ok", "service": "reporting-service"}


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    docs = db.query(Document).filter(Document.user_id == user_id).all()
    analyses = db.query(Analysis).filter(Analysis.user_id == user_id).all()

    out_of_range = [a for a in analyses if a.status in ("HIGH", "LOW")]
    by_type = defaultdict(int)
    for d in docs:
        by_type[d.doc_type or "UNKNOWN"] += 1

    last_dates = [a.analysis_date for a in analyses if a.analysis_date]
    last_analysis = max(last_dates).isoformat() if last_dates else None

    total = len(analyses)
    return {
        "total_documents": len(docs),
        "total_analyses": total,
        "out_of_range_count": len(out_of_range),
        "out_of_range_percent": round(100 * len(out_of_range) / total, 1) if total else 0.0,
        "last_analysis_date": last_analysis,
        "documents_by_type": dict(by_type),
    }


@router.get("/evolution/{analysis_name}")
def evolution(analysis_name: str, db: Session = Depends(get_db),
              user_id: str = Depends(get_current_user_id)):
    rows = (db.query(Analysis)
              .filter(Analysis.user_id == user_id,
                      Analysis.analysis_name.ilike(analysis_name))
              .all())
    points = [{"date": a.analysis_date.isoformat() if a.analysis_date else None,
               "value": a.value, "status": a.status,
               "ref_min": a.ref_min, "ref_max": a.ref_max}
              for a in rows if a.value is not None]
    points.sort(key=lambda p: p["date"] or "")

    values = [p["value"] for p in points]
    ref_min = next((p["ref_min"] for p in points if p["ref_min"] is not None), None)
    ref_max = next((p["ref_max"] for p in points if p["ref_max"] is not None), None)

    return {
        "analysis_name": analysis_name,
        "points": points,
        "min": min(values) if values else None,
        "max": max(values) if values else None,
        "avg": round(mean(values), 2) if values else None,
        "ref_min": ref_min,
        "ref_max": ref_max,
    }


@router.get("/all-analyses")
def all_analyses(db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    rows = (db.query(Analysis)
              .filter(Analysis.user_id == user_id)
              .order_by(Analysis.analysis_date.desc().nullslast())
              .all())
    # Regroupement par nom d'analyse
    grouped = defaultdict(list)
    for a in rows:
        grouped[a.analysis_name].append({
            "value": a.value, "unit": a.unit, "status": a.status,
            "date": a.analysis_date.isoformat() if a.analysis_date else None,
        })
    return {"analyses": [{"name": name, "count": len(v), "history": v}
                         for name, v in grouped.items()]}


@router.get("/export/excel")
def export_excel(db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    analyses = (db.query(Analysis)
                  .filter(Analysis.user_id == user_id)
                  .order_by(Analysis.analysis_name, Analysis.analysis_date)
                  .all())
    data = build_excel(analyses)
    return StreamingResponse(
        iter([data]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=mes_analyses.xlsx"},
    )
