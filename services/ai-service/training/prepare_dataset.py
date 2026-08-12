"""Genere 200 documents synthetiques annotes pour fine-tuner LayoutLMv3.

Chaque document est une image de "bilan sanguin" avec, pour chaque mot :
  - le texte
  - la bbox [x1,y1,x2,y2]
  - un label BIO (O, B/I-ANALYSE, B/I-VALEUR, B/I-UNITE, B/I-REFERENCE, B/I-PATIENT, B/I-DATE)

Sortie : dataset/ (images + annotations.jsonl)
Usage :  python prepare_dataset.py --n 200 --out dataset
"""
import os
import json
import random
import argparse
from PIL import Image, ImageDraw, ImageFont

ANALYSES = [
    ("Glycemie", "g/L", (0.70, 1.30)),
    ("Hemoglobine", "g/dL", (10.0, 18.0)),
    ("Cholesterol", "g/L", (1.2, 2.8)),
    ("Triglycerides", "g/L", (0.5, 2.5)),
    ("Creatinine", "mg/L", (5.0, 15.0)),
    ("Uree", "g/L", (0.15, 0.55)),
    ("TSH", "mUI/L", (0.2, 6.0)),
    ("Vitamine D", "ng/mL", (10.0, 80.0)),
    ("Leucocytes", "10^3/uL", (3.0, 12.0)),
    ("Plaquettes", "10^3/uL", (120.0, 450.0)),
]
NAMES = ["Martin Dupont", "Sophie Bernard", "Ahmed Alami", "Fatima Zahra",
         "Jean Petit", "Laura Garcia", "Yassine Idrissi", "Marie Leroy"]
LABS = ["Labo Central", "BioSante", "Institut Pasteur", "MedLab Plus"]

LABEL_LIST = ["O", "B-ANALYSE", "I-ANALYSE", "B-VALEUR", "I-VALEUR",
              "B-UNITE", "I-UNITE", "B-REFERENCE", "I-REFERENCE",
              "B-PATIENT", "I-PATIENT", "B-DATE", "I-DATE"]


def _font(size=18):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def add_words(draw, x, y, text, label_prefix, font, words):
    """Ajoute chaque mot avec sa bbox et son label BIO."""
    cursor = x
    for i, tok in enumerate(text.split()):
        bbox = draw.textbbox((cursor, y), tok, font=font)
        if label_prefix == "O":
            lab = "O"
        else:
            lab = f"B-{label_prefix}" if i == 0 else f"I-{label_prefix}"
        words.append({"word": tok, "bbox": [int(b) for b in bbox], "label": lab})
        cursor = bbox[2] + 8
    return cursor


def generate_document(idx: int, out_dir: str):
    W, H = 800, 1000
    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)
    font = _font(18)
    title_font = _font(24)
    words = []

    draw.text((40, 30), "BILAN SANGUIN", fill="black", font=title_font)

    y = 90
    add_words(draw, 40, y, "Patient :", "O", font, words)
    add_words(draw, 160, y, random.choice(NAMES), "PATIENT", font, words)

    y += 35
    date = f"{random.randint(1,28):02d}/{random.randint(1,12):02d}/2025"
    add_words(draw, 40, y, "Date :", "O", font, words)
    add_words(draw, 160, y, date, "DATE", font, words)

    y += 35
    add_words(draw, 40, y, "Laboratoire :", "O", font, words)
    add_words(draw, 200, y, random.choice(LABS), "O", font, words)

    y += 60
    sample = random.sample(ANALYSES, k=random.randint(4, 8))
    for name, unit, (lo, hi) in sample:
        val = round(random.uniform(lo, hi), 2)
        x = add_words(draw, 40, y, name, "ANALYSE", font, words)
        x = add_words(draw, x + 10, y, ":", "O", font, words)
        x = add_words(draw, x + 10, y, str(val), "VALEUR", font, words)
        x = add_words(draw, x + 10, y, unit, "UNITE", font, words)
        y += 40

    img_path = os.path.join(out_dir, "images", f"doc_{idx:04d}.png")
    img.save(img_path)
    return {
        "image": f"images/doc_{idx:04d}.png",
        "width": W, "height": H,
        "words": [w["word"] for w in words],
        "bboxes": [w["bbox"] for w in words],
        "labels": [w["label"] for w in words],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--out", default="dataset")
    args = ap.parse_args()

    os.makedirs(os.path.join(args.out, "images"), exist_ok=True)
    with open(os.path.join(args.out, "annotations.jsonl"), "w", encoding="utf-8") as f:
        for i in range(args.n):
            record = generate_document(i, args.out)
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    with open(os.path.join(args.out, "labels.json"), "w") as f:
        json.dump(LABEL_LIST, f)

    print(f"{args.n} documents generes dans '{args.out}/'")


if __name__ == "__main__":
    main()
