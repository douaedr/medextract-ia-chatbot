# MedExtract AI - DEV 3 : IA & Chatbot

- **ai-service** (8084) : extraction d'entites medicales (regex + LayoutLMv3).
- **chatbot-service** (8085) : assistant RAG (Mistral/Ollama) avec garde-fous.

## Structure
```
dev3/
├── services/ai-service/
│   ├── app/                      # FastAPI 8084
│   │   └── extraction/           # regex + reference ranges + layoutlm
│   └── training/                 # prepare_dataset.py + train_layoutlmv3.py
├── services/chatbot-service/
│   └── app/rag/                  # knowledge_base, retriever, llm, safety
└── docs/AI_CHATBOT_SERVICE.md
```

## Points cles pour le jury
- Repli automatique regex si le modele n'est pas entraine (demo toujours OK).
- F1 affiche a la fin de l'entrainement (objectif >= 0.75).
- Chatbot : refus de diagnostic + disclaimer systematique (a montrer en live).

## Lancer avec tout le projet
Placer `dev3/` a cote de `dev1/`, `dev2/`, `dev4/`, puis depuis `dev1/` :
`docker compose up --build`.

## Entrainer le modele
Voir `services/ai-service/training/README_TRAINING.md`.
