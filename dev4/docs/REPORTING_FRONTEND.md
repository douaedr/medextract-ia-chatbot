# Reporting Service & Frontend - Documentation (DEV 4)

## Reporting Service (port 8086)

### Endpoints
| Methode | URL                                | Description                       |
|---------|------------------------------------|-----------------------------------|
| GET     | /api/reports/dashboard             | Stats globales du patient         |
| GET     | /api/reports/evolution/{analysis}  | Evolution d'une analyse           |
| GET     | /api/reports/all-analyses          | Resume de toutes les analyses     |
| GET     | /api/reports/export/excel          | Export Excel colorie par statut   |
| GET     | /api/reports/health                | Etat du service                   |

### Dashboard renvoie
`total_documents, total_analyses, out_of_range_count, out_of_range_percent,
last_analysis_date, documents_by_type`.

### Evolution renvoie
Points tries par date + `min / max / avg` + `ref_min / ref_max` (pour tracer les
lignes de reference sur le graphique).

### Export Excel (openpyxl)
- En-tetes bleu fonce (`1F4E78`), police blanche, gras.
- Cellules colorees selon le statut : **vert** NORMAL, **rouge** HIGH, **bleu** LOW.

## Frontend React TypeScript

### Stack
React 18 + TypeScript, React Router v6, Axios, Recharts, react-dropzone, Vite.

### Pages
| Route             | Contenu                                                        |
|-------------------|----------------------------------------------------------------|
| /login            | Connexion, erreur si mauvais identifiants, redirect si connecte|
| /register         | Inscription + validation cote client                           |
| (layout sidebar)  | Navigation fixe, nom utilisateur, lien actif, deconnexion      |
| /dashboard        | 4 cartes stats, camembert types docs, barres top analyses      |
| /documents        | Drag-and-drop, barre progression, tableau + filtres + actions  |
| /documents/:id    | Infos doc, texte OCR, tableau analyses (confiance coloree)     |
| /analyses         | Liste cliquable + graphique evolution avec zones de reference  |
| /chat             | Messagerie, questions rapides, indicateur de chargement        |
| /profile          | Informations de l'utilisateur connecte                         |

### Lancer le frontend en dev
```bash
cd frontend
npm install
npm run dev        # http://localhost:5173  (proxy /api -> http://localhost:8080)
```
> Necessite que l'API Gateway (DEV 1) tourne sur le port 8080.

### Build production (dans Docker)
Le `Dockerfile` compile puis sert via nginx. Le nginx du frontend proxifie
`/api/` vers l'API Gateway.
