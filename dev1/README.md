# MedExtract AI - DEV 1 : Infrastructure & Auth

Responsable de l'ossature du projet : Docker, PostgreSQL, RabbitMQ, l'API
Gateway Nginx et le **Auth Service** (authentification JWT).

## Contenu de ce dossier
```
dev1/
├── docker-compose.yml          # Orchestration des 6 microservices + infra
├── .env.example / .env         # Variables d'environnement (JWT partage, DB...)
├── nginx/nginx.conf            # API Gateway (point d'entree unique :8080)
├── database/init.sql           # TOUTES les tables creees au 1er demarrage
├── services/auth-service/      # FastAPI - port 8081
└── docs/AUTH_SERVICE.md        # Documentation du service
```

## Lancer TOUT le projet (les 4 parties reunies)
Le `docker-compose.yml` reference les dossiers `../dev2`, `../dev3`, `../dev4`.
Pour un build complet, placer les 4 dossiers cote a cote :
```
medextract/
├── dev1/   ← vous etes ici
├── dev2/
├── dev3/
└── dev4/
```
Puis, depuis `dev1/` :
```bash
cp .env.example .env       # ajuster les secrets si besoin
docker compose up --build
```

| Service            | URL directe            | Via Gateway (8080)          |
|--------------------|------------------------|-----------------------------|
| Auth               | http://localhost:8081  | /api/auth/...               |
| Documents          | http://localhost:8082  | /api/documents/...          |
| OCR                | http://localhost:8083  | /api/ocr/...                |
| AI                 | http://localhost:8084  | /api/ai/...                 |
| Chatbot            | http://localhost:8085  | /api/chat/...               |
| Reporting          | http://localhost:8086  | /api/reports/...            |
| Frontend           | http://localhost:3000  | -                           |
| RabbitMQ (admin)   | http://localhost:15672 | -                           |

## Lancer UNIQUEMENT ma partie (dev en solo)
```bash
docker compose up --build postgres rabbitmq auth-service nginx
```

## Premier compte
Aucun compte n'est cree en dur. Inscrivez-vous via l'interface (`/register`) ou
via Swagger `POST /api/auth/register`, par exemple `admin@medextract.ai` /
`Admin1234` avec le role `ADMIN`.

## Contrat pour les autres services
Tout service qui doit proteger ses routes verifie le JWT avec la MEME
`JWT_SECRET_KEY` que celle du `.env`. Details dans `docs/AUTH_SERVICE.md`.
