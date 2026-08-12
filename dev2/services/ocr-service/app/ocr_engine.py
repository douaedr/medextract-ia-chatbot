"""Moteur OCR base sur PaddleOCR + pdf2image.

Chaque mot detecte est retourne au format :
    {"word": str, "confidence": float, "bbox": [x1,y1,x2,y2], "page": int}
bbox = coin superieur-gauche + coin inferieur-droit, en pixels.
"""
import time
import numpy as np
from PIL import Image
from pdf2image import convert_from_path
from paddleocr import PaddleOCR

from .config import settings

# Le modele PaddleOCR est charge UNE seule fois (couteux au demarrage).
_ocr_engine = None

def get_engine() -> PaddleOCR:
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = PaddleOCR(use_angle_cls=True, lang=settings.OCR_LANG,
                                show_log=False)
    return _ocr_engine


def _quad_to_bbox(quad) -> list[int]:
    """Convertit un quadrilatere PaddleOCR [[x,y]*4] en [x1,y1,x2,y2]."""
    xs = [p[0] for p in quad]
    ys = [p[1] for p in quad]
    return [int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))]


def _ocr_image(pil_img: Image.Image, page: int) -> list[dict]:
    engine = get_engine()
    arr = np.array(pil_img.convert("RGB"))
    result = engine.ocr(arr, cls=True)
    words = []
    # result = [ [ [quad, (text, conf)], ... ] ]  (une liste par image)
    if not result or result[0] is None:
        return words
    for line in result[0]:
        quad, (text, conf) = line[0], line[1]
        # Une "ligne" PaddleOCR peut contenir plusieurs mots : on decoupe.
        for token in str(text).split():
            words.append({
                "word": token,
                "confidence": round(float(conf), 4),
                "bbox": _quad_to_bbox(quad),
                "page": page,
            })
    return words


def run_ocr(file_path: str, mime_type: str) -> dict:
    """Retourne {raw_text, words, page_count, processing_time}."""
    start = time.time()
    all_words: list[dict] = []
    page_count = 1

    if mime_type == "application/pdf" or file_path.lower().endswith(".pdf"):
        pages = convert_from_path(file_path, dpi=settings.PDF_DPI)
        page_count = len(pages)
        for i, page_img in enumerate(pages):
            all_words.extend(_ocr_image(page_img, page=i))
    else:
        img = Image.open(file_path)
        all_words.extend(_ocr_image(img, page=0))

    raw_text = " ".join(w["word"] for w in all_words)
    return {
        "raw_text": raw_text,
        "words": all_words,
        "page_count": page_count,
        "processing_time": round(time.time() - start, 3),
    }
