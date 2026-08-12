"""Phase 1 - Extraction par regles (regex), sans entrainement.

Reconnait les patterns du type :
    'Glycemie : 1.15 g/L'
    'Hemoglobine : 14.2 g/dL (12.0 - 16.0)'
et extrait aussi : date, patient, medecin, laboratoire.
Confiance fixe a 0.70 (indique l'incertitude des regles).
"""
import re
from datetime import datetime
from .reference_ranges import get_reference, compute_status, normalize_name

CONFIDENCE = 0.70

# Nom d'analyse : lettres/espaces ; valeur : nombre ; unite ; reference optionnelle
ANALYSIS_PATTERN = re.compile(
    r"(?P<name>[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\s\-]{2,40}?)\s*[:=]\s*"
    r"(?P<value>\d+[.,]?\d*)\s*"
    r"(?P<unit>[a-zA-Zµ%/^0-9\.]{1,12})?"
    r"(?:\s*[\(\[]\s*(?P<rmin>\d+[.,]?\d*)\s*[-a–]\s*(?P<rmax>\d+[.,]?\d*)\s*[\)\]])?",
    re.UNICODE,
)

DATE_PATTERN = re.compile(r"\b(\d{2}[/\-.]\d{2}[/\-.]\d{2,4})\b")
PATIENT_PATTERN = re.compile(r"(?:patient|nom)\s*[:=]?\s*([A-ZÀ-Ÿ][A-Za-zÀ-ÿ\s\-]{2,40})", re.I)
DOCTOR_PATTERN = re.compile(r"(?:dr|docteur|medecin|prescripteur)\s*\.?\s*[:=]?\s*([A-ZÀ-Ÿ][A-Za-zÀ-ÿ\s\-]{2,40})", re.I)
LAB_PATTERN = re.compile(r"(?:laboratoire|labo|lab)\s*[:=]?\s*([A-ZÀ-Ÿ][A-Za-zÀ-ÿ0-9\s\-]{2,40})", re.I)

# Mots a exclure : ne sont pas des analyses
STOPWORDS = {"date", "patient", "nom", "age", "sexe", "medecin", "docteur",
             "laboratoire", "page", "tel", "telephone", "adresse", "reference"}


def _to_float(s):
    if s is None:
        return None
    try:
        return float(s.replace(",", "."))
    except ValueError:
        return None


def _parse_date(text: str):
    m = DATE_PATTERN.search(text)
    if not m:
        return None
    raw = m.group(1).replace(".", "/").replace("-", "/")
    for fmt in ("%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def _first_group(pattern, text):
    m = pattern.search(text)
    return m.group(1).strip() if m else None


def extract_from_text(text: str) -> dict:
    """Retourne {patient_name, doctor_name, lab_name, analysis_date, analyses[]}."""
    analyses = []
    analysis_date = _parse_date(text)

    for m in ANALYSIS_PATTERN.finditer(text):
        name = m.group("name").strip()
        if name.lower() in STOPWORDS or len(name) < 3:
            continue
        value = _to_float(m.group("value"))
        if value is None:
            continue
        unit = (m.group("unit") or "").strip() or None
        ref_min = _to_float(m.group("rmin"))
        ref_max = _to_float(m.group("rmax"))

        # Completer avec les normes connues si absentes du document
        if ref_min is None or ref_max is None:
            r_min, r_max, default_unit = get_reference(name)
            ref_min = ref_min if ref_min is not None else r_min
            ref_max = ref_max if ref_max is not None else r_max
            if unit is None:
                unit = default_unit

        status = compute_status(value, ref_min, ref_max)
        analyses.append({
            "analysis_name": name.title(),
            "value": value,
            "unit": unit,
            "ref_min": ref_min,
            "ref_max": ref_max,
            "status": status,
            "confidence": CONFIDENCE,
            "bbox": None,
            "analysis_date": analysis_date,
        })

    return {
        "patient_name": _first_group(PATIENT_PATTERN, text),
        "doctor_name": _first_group(DOCTOR_PATTERN, text),
        "lab_name": _first_group(LAB_PATTERN, text),
        "analysis_date": analysis_date,
        "analyses": analyses,
        "model_version": "regex-v1",
    }
