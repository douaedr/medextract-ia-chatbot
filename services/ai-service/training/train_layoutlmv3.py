"""Fine-tuning de microsoft/layoutlmv3-base sur le dataset synthetique.

Etapes :
  1. Charger dataset/annotations.jsonl (mots + bbox + labels BIO).
  2. Encoder avec LayoutLMv3Processor (apply_ocr=False, on fournit deja les mots).
  3. Entrainer LayoutLMv3ForTokenClassification.
  4. Evaluer avec seqeval : Precision, Recall, F1  (objectif F1 >= 0.75).
  5. Sauvegarder dans /app/model/layoutlmv3-medical/.

Usage : python train_layoutlmv3.py --data dataset --out /app/model/layoutlmv3-medical --epochs 8
"""
import os
import json
import argparse
import numpy as np
from PIL import Image

import torch
from datasets import Dataset
from transformers import (LayoutLMv3Processor, LayoutLMv3ForTokenClassification,
                          TrainingArguments, Trainer)
from seqeval.metrics import precision_score, recall_score, f1_score, classification_report


def normalize_bbox(bbox, w, h):
    x1, y1, x2, y2 = bbox
    return [int(1000*x1/w), int(1000*y1/h), int(1000*x2/w), int(1000*y2/h)]


def load_records(data_dir):
    recs = []
    with open(os.path.join(data_dir, "annotations.jsonl"), encoding="utf-8") as f:
        for line in f:
            recs.append(json.loads(line))
    labels = json.load(open(os.path.join(data_dir, "labels.json")))
    return recs, labels


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="dataset")
    ap.add_argument("--out", default="/app/model/layoutlmv3-medical")
    ap.add_argument("--epochs", type=int, default=8)
    ap.add_argument("--base", default="microsoft/layoutlmv3-base")
    args = ap.parse_args()

    records, label_list = load_records(args.data)
    label2id = {l: i for i, l in enumerate(label_list)}
    id2label = {i: l for l, i in label2id.items()}

    # Split 80/20
    split = int(len(records) * 0.8)
    train_recs, eval_recs = records[:split], records[split:]

    processor = LayoutLMv3Processor.from_pretrained(args.base, apply_ocr=False)

    def build(recs):
        data = {"image": [], "words": [], "boxes": [], "labels": []}
        for r in recs:
            img = Image.open(os.path.join(args.data, r["image"])).convert("RGB")
            w, h = r["width"], r["height"]
            data["image"].append(img)
            data["words"].append(r["words"])
            data["boxes"].append([normalize_bbox(b, w, h) for b in r["bboxes"]])
            data["labels"].append([label2id[l] for l in r["labels"]])
        return data

    def encode(examples):
        enc = processor(examples["image"], examples["words"],
                        boxes=examples["boxes"], word_labels=examples["labels"],
                        truncation=True, padding="max_length", return_tensors="pt")
        return {k: v for k, v in enc.items()}

    train_ds = Dataset.from_dict(build(train_recs)).map(
        encode, batched=True, batch_size=8,
        remove_columns=["image", "words", "boxes", "labels"])
    eval_ds = Dataset.from_dict(build(eval_recs)).map(
        encode, batched=True, batch_size=8,
        remove_columns=["image", "words", "boxes", "labels"])
    train_ds.set_format("torch")
    eval_ds.set_format("torch")

    model = LayoutLMv3ForTokenClassification.from_pretrained(
        args.base, num_labels=len(label_list), id2label=id2label, label2id=label2id)

    def compute_metrics(p):
        preds = np.argmax(p.predictions, axis=2)
        true_labels, true_preds = [], []
        for pred, lab in zip(preds, p.label_ids):
            tl, tp = [], []
            for pr, la in zip(pred, lab):
                if la != -100:
                    tl.append(id2label[la]); tp.append(id2label[pr])
            true_labels.append(tl); true_preds.append(tp)
        return {
            "precision": precision_score(true_labels, true_preds),
            "recall": recall_score(true_labels, true_preds),
            "f1": f1_score(true_labels, true_preds),
        }

    targs = TrainingArguments(
        output_dir="./_train_tmp",
        num_train_epochs=args.epochs,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        learning_rate=5e-5,
        eval_strategy="epoch",
        save_strategy="no",
        logging_steps=20,
        report_to="none",
    )
    trainer = Trainer(model=model, args=targs, train_dataset=train_ds,
                      eval_dataset=eval_ds, compute_metrics=compute_metrics)

    trainer.train()
    metrics = trainer.evaluate()
    print("\n=== Evaluation finale ===")
    print(f"Precision : {metrics['eval_precision']:.4f}")
    print(f"Recall    : {metrics['eval_recall']:.4f}")
    print(f"F1-Score  : {metrics['eval_f1']:.4f}  (objectif >= 0.75)")

    os.makedirs(args.out, exist_ok=True)
    model.save_pretrained(args.out)
    processor.save_pretrained(args.out)
    print(f"\nModele sauvegarde dans {args.out}")


if __name__ == "__main__":
    main()
