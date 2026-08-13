# MedExtract AI - DEV 4 : Reporting & Frontend

- **reporting-service** (8086) : stats, evolution temporelle, export Excel.
- **frontend** : application React 18 + TypeScript (l'interface jugee par le jury).

## Structure
```
dev4/
├── services/reporting-service/   # FastAPI 8086 (openpyxl)
├── frontend/                     # React + TS + Vite + Recharts
│   ├── src/pages/                # Login, Dashboard, Documents, Analyses, Chat...
│   ├── src/components/           # Layout (sidebar), ProtectedRoute
│   ├── src/context/AuthContext   # gestion du JWT
│   └── src/api/client.ts         # axios + intercepteurs
└── docs/REPORTING_FRONTEND.md
```

## Lancer le frontend seul (dev)
```bash
cd frontend && npm install && npm run dev
# http://localhost:5173  (necessite l'API Gateway sur :8080)
```

## Integration complete
Placer `dev4/` a cote de `dev1/`, `dev2/`, `dev3/`, puis depuis `dev1/` :
`docker compose up --build`.  Frontend accessible sur http://localhost:3000.

## Points forts pour le jury
- Interface responsive lisible en 1366x768.
- Graphiques Recharts (camembert, barres, aire avec lignes de reference).
- Export Excel colorise telecharge en un clic.
