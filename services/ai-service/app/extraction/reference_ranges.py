"""Normes de reference pour les analyses medicales courantes.
Sert a calculer le statut NORMAL / HIGH / LOW quand aucune reference n'est
presente dans le document.
"""
# nom_normalise -> (ref_min, ref_max, unite_par_defaut)
REFERENCE_RANGES = {
    "glycemie":       (0.70, 1.10, "g/L"),
    "hemoglobine":    (12.0, 16.0, "g/dL"),
    "cholesterol":    (0.0, 2.0, "g/L"),
    "cholesterol hdl":(0.40, 0.60, "g/L"),
    "cholesterol ldl":(0.0, 1.60, "g/L"),
    "triglycerides":  (0.0, 1.50, "g/L"),
    "creatinine":     (6.0, 12.0, "mg/L"),
    "uree":           (0.15, 0.45, "g/L"),
    "tsh":            (0.40, 4.0, "mUI/L"),
    "vitamine d":     (30.0, 100.0, "ng/mL"),
    "hba1c":          (4.0, 6.0, "%"),
    "leucocytes":     (4.0, 10.0, "10^3/uL"),
    "plaquettes":     (150.0, 400.0, "10^3/uL"),
}

# Synonymes -> nom normalise
ALIASES = {
    "glucose": "glycemie",
    "hb": "hemoglobine",
    "hgb": "hemoglobine",
    "chol": "cholesterol",
    "hdl": "cholesterol hdl",
    "ldl": "cholesterol ldl",
    "tg": "triglycerides",
    "crea": "creatinine",
    "25-oh": "vitamine d",
    "vit d": "vitamine d",
}

def normalize_name(name: str) -> str:
    n = name.strip().lower()
    return ALIASES.get(n, n)

def get_reference(name: str):
    """Retourne (ref_min, ref_max, unite) ou (None, None, None)."""
    n = normalize_name(name)
    if n in REFERENCE_RANGES:
        return REFERENCE_RANGES[n]
    return (None, None, None)

def compute_status(value, ref_min, ref_max) -> str:
    if value is None or ref_min is None or ref_max is None:
        return "UNKNOWN"
    if value < ref_min:
        return "LOW"
    if value > ref_max:
        return "HIGH"
    return "NORMAL"
