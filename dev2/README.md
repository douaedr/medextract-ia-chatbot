# MedExtract AI - DEV 2 : Documents & OCR

Deux microservices :
- **document-service** (8082) : upload, stockage, gestion des documents.
- **ocr-service** (8083) : extraction texte + positions via PaddleOCR.

## Structure
```
dev2/
├── docker-compose.dev2.yml     # lancer ma partie en solo
├── make_test_token.py          # generer un JWT de test
├── services/document-service/  # FastAPI 8082
├── services/ocr-service/       # FastAPI 8083 (PaddleOCR + pdf2image)
└── docs/DOCUMENT_OCR_SERVICE.md
```

## Lancer en solo
```bash
docker compose -f docker-compose.dev2.yml up --build
```
> Le premier demarrage de l'OCR telecharge les modeles PaddleOCR (~ quelques
> minutes selon la connexion).

## Integration complete
Placer `dev2/` a cote de `dev1/`, `dev3/`, `dev4/` puis lancer depuis `dev1/` :
`docker compose up --build`.

## Contrats d'interface
- Recu de Document -> OCR : `POST /api/ocr/process {document_id, file_path, mime_type}`
- Envoye Document -> AI  : `POST /api/ai/extract {document_id, file_path}`
- JWT verifie localement avec la meme `JWT_SECRET_KEY` que DEV 1.
