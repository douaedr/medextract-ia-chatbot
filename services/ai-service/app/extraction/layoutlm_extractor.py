"""Phase 2 - Extraction avec LayoutLMv3 fine-tune.

Le modele est charge au demarrage du service SI le dossier MODEL_DIR existe.
Sinon `model_loaded = False` et l'extraction retombe sur les regles regex.

LayoutLMv3 combine texte + position (bbox) de chaque mot pour predire un label
BIO : O, B/I-ANALYSE, B/I-VALEUR, B/I-UNITE, B/I-REFERENCE, B/I-PATIENT, B/I-DATE.
"""
import os
from ..config import settings

_model = None
_processor = None
_loaded = False
_id2label = None

LABELS = ["O",
          "B-ANALYSE", "I-ANALYSE", "B-VALEUR", "I-VALEUR",
          "B-UNITE", "I-UNITE", "B-REFERENCE", "I-REFERENCE",
          "B-PATIENT", "I-PATIENT", "B-DATE", "I-DATE"]


def load_model():
    """Charge le modele une seule fois. Retourne True si charge."""
    global _model, _processor, _loaded, _id2label
    if _loaded:
        return True
    if not os.path.isdir(settings.MODEL_DIR):
        return False
    try:
        from transformers import (LayoutLMv3ForTokenClassification,
                                  LayoutLMv3Processor)
        _processor = LayoutLMv3Processor.from_pretrained(settings.MODEL_DIR, apply_ocr=False)
        _model = LayoutLMv3ForTokenClassification.from_pretrained(settings.MODEL_DIR)
        _model.eval()
        _id2label = _model.config.id2label
        _loaded = True
        return True
    except Exception as e:
        print(f"[layoutlm] chargement impossible : {e}")
        return False


def is_loaded() -> bool:
    return _loaded


def _normalize_bbox(bbox, width, height):
    """LayoutLMv3 attend des coordonnees normalisees sur 0-1000."""
    x1, y1, x2, y2 = bbox
    return [
        int(1000 * x1 / width), int(1000 * y1 / height),
        int(1000 * x2 / width), int(1000 * y2 / height),
    ]


def extract_with_model(words: list[dict], image) -> dict:
    """words = [{word, confidence, bbox, page}], image = PIL.Image (page 0).
    Retourne le meme format que le regex_extractor (dict avec analyses[])."""
    import torch

    if not _loaded:
        raise RuntimeError("Modele non charge")

    width, height = image.size
    tokens = [w["word"] for w in words]
    boxes = [_normalize_bbox(w["bbox"], width, height) for w in words]

    encoding = _processor(image, tokens, boxes=boxes, return_tensors="pt",
                          truncation=True, padding="max_length")
    with torch.no_grad():
        outputs = _model(**{k: v for k, v in encoding.items()
                            if k in ("input_ids", "attention_mask", "bbox", "pixel_values")})
    predictions = outputs.logits.argmax(-1).squeeze().tolist()
    word_ids = encoding.word_ids(0)

    # Regrouper les predictions au niveau du mot (1er sous-token)
    labels = []
    seen = set()
    for pred, wid in zip(predictions, word_ids):
        if wid is None or wid in seen:
            continue
        seen.add(wid)
        labels.append((wid, _id2label[pred]))

    return _assemble_entities(words, labels)


def _assemble_entities(words, labels):
    """Reconstruit les analyses a partir des labels BIO."""
    current = {"name": [], "value": None, "unit": None, "ref": []}
    analyses = []
    meta = {"patient_name": None, "doctor_name": None, "lab_name": None,
            "analysis_date": None}

    def flush():
        if current["name"]:
            from .reference_ranges import get_reference, compute_status
            name = " ".join(current["name"])
            value = None
            try:
                value = float(str(current["value"]).replace(",", ".")) if current["value"] else None
            except ValueError:
                value = None
            r_min, r_max, default_unit = get_reference(name)
            unit = current["unit"] or default_unit
            status = compute_status(value, r_min, r_max)
            analyses.append({
                "analysis_name": name.title(), "value": value, "unit": unit,
                "ref_min": r_min, "ref_max": r_max, "status": status,
                "confidence": 0.85, "bbox": None, "analysis_date": None,
            })
        current["name"], current["value"], current["unit"], current["ref"] = [], None, None, []

    for (wid, label), w in zip(labels, words):
        tok = w["word"]
        if label == "B-ANALYSE":
            flush(); current["name"] = [tok]
        elif label == "I-ANALYSE":
            current["name"].append(tok)
        elif label in ("B-VALEUR", "I-VALEUR"):
            current["value"] = tok
        elif label in ("B-UNITE", "I-UNITE"):
            current["unit"] = tok
        elif label == "B-PATIENT":
            meta["patient_name"] = tok
        elif label == "B-DATE":
            meta["analysis_date"] = tok
    flush()

    meta["analyses"] = analyses
    meta["model_version"] = "layoutlmv3-medical"
    return meta
