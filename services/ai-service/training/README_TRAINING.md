# Entrainement LayoutLMv3 (DEV 3)

## 1. Generer les 200 documents annotes
```bash
cd services/ai-service/training
pip install pillow
python prepare_dataset.py --n 200 --out dataset
```

## 2. Fine-tuner le modele
```bash
pip install torch transformers datasets seqeval
python train_layoutlmv3.py --data dataset \
    --out /app/model/layoutlmv3-medical --epochs 8
```
La sortie affiche Precision / Recall / F1 (objectif **F1 >= 0.75**).

## 3. Utiliser le modele
Au demarrage, l'AI Service detecte `/app/model/layoutlmv3-medical/` et charge
le modele automatiquement. `GET /api/ai/model-info` renvoie alors
`model_loaded: true`. Sinon, l'extraction utilise les regles regex (0.70).

> Astuce : entrainer sur GPU (CUDA) pour aller beaucoup plus vite.
