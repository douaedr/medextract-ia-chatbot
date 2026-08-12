# Document & OCR Services - Documentation (DEV 2)

## 1. Document Service (port 8082)
Gere l'upload, le stockage et la gestion des documents medicaux.

### Endpoints
| Methode | URL                                | Description               |
|---------|------------------------------------|---------------------------|
| POST    | /api/documents/upload              | Upload PDF/JPG/PNG         |
| GET     | /api/documents/                    | Liste de mes documents    |
| GET     | /api/documents/{id}                | Detail d'un document      |
| DELETE  | /api/documents/{id}                | Supprimer                 |
| GET     | /api/documents/{id}/download       | Telecharger l'original    |
| GET     | /api/documents/health              | Etat du service           |

### Regles
- Types acceptes : `application/pdf`, `image/jpeg`, `image/png`. Sinon **400**.
- Taille max : **20 MB**. Sinon **400**.
- Stockage : `/app/uploads/{user_id}/{uuid}.ext`.
- Apres upload -> pipeline **OCR puis IA** declenche en tache de fond.
- Statut du document : `PENDING -> OCR_DONE -> AI_DONE` (ou `ERROR`).
- Isolation : un utilisateur ne voit QUE ses documents (sinon **404**).

## 2. OCR Service (port 8083)

### Comment fonctionne PaddleOCR
PaddleOCR detecte les zones de texte (detection) puis les lit (reconnaissance).
Le modele est charge **une seule fois** au demarrage (couteux). On l'utilise en
francais (`lang="fr"`).

### PDF vs image
- **PDF** : chaque page est convertie en image avec `pdf2image` a **DPI=200**,
  puis passee a PaddleOCR. L'attribut `page` (0,1,2...) est conserve par mot.
- **Image JPG/PNG** : PaddleOCR est applique directement (page 0).

### Format des bounding boxes
Pour chaque mot :
```json
{"word": "Glycemie", "confidence": 0.9876, "bbox": [45, 210, 180, 235], "page": 0}
```
`bbox = [x1, y1, x2, y2]` = coin superieur-gauche et coin inferieur-droit en
pixels. PaddleOCR renvoie un quadrilatere ; on le convertit en rectangle
englobant (`min/max` des x et y). Ces coordonnees sont ensuite reutilisees par
LayoutLMv3 (DEV 3).

### Ameliorer la qualite OCR
- Augmenter le **DPI** (200 -> 300) pour les scans flous (plus lent).
- Pretraitement : passage en niveaux de gris, binarisation, redressement.
- Activer `use_angle_cls=True` pour les documents legerement tournes.

### Endpoints
| Methode | URL                     | Description                    |
|---------|-------------------------|--------------------------------|
| POST    | /api/ocr/process        | Lancer l'OCR sur un document   |
| GET     | /api/ocr/{document_id}  | Recuperer le resultat OCR      |
| GET     | /api/ocr/health         | Etat du service                |

### Exemple de resultat sur un bilan sanguin
Entree (image) : ligne "Glycemie : 1.15 g/L".
Sortie `words` (extrait) :
```json
[
  {"word": "Glycemie", "confidence": 0.99, "bbox": [45,210,180,235], "page": 0},
  {"word": ":",        "confidence": 0.95, "bbox": [188,210,196,235], "page": 0},
  {"word": "1.15",     "confidence": 0.98, "bbox": [205,210,255,235], "page": 0},
  {"word": "g/L",      "confidence": 0.97, "bbox": [262,210,300,235], "page": 0}
]
```

## 3. Lancer ma partie seule
```bash
cd dev2
docker compose -f docker-compose.dev2.yml up --build
# Swagger Document : http://localhost:8082/docs
# Swagger OCR      : http://localhost:8083/docs
```
Pour tester l'upload sans Auth Service, generer un token :
```bash
# recuperer l'id du compte admin dans la table users, puis :
python make_test_token.py <user_id>
# coller le token dans le bouton "Authorize" de Swagger
```
