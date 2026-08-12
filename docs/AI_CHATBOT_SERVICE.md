# AI & Chatbot Services - Documentation (DEV 3)

## AI Service (port 8084)

### Deux phases d'extraction
**Phase 1 - Regles (regex)** : sans entrainement. Reconnait
`Analyse : valeur unite (ref_min - ref_max)`, extrait patient/medecin/labo/date,
calcule le statut NORMAL/HIGH/LOW, confiance fixe **0.70**.

**Phase 2 - LayoutLMv3** : fine-tuning de `microsoft/layoutlmv3-base` avec les
mots + coordonnees bbox de l'OCR. Labels BIO :
`O, B/I-ANALYSE, B/I-VALEUR, B/I-UNITE, B/I-REFERENCE, B/I-PATIENT, B/I-DATE`.
Objectif **F1 >= 0.75**. Voir `training/README_TRAINING.md`.

> Le service charge le modele au demarrage s'il existe, sinon il utilise les
> regles. `GET /api/ai/model-info` renvoie `model_loaded: true/false`.

### Endpoints
| Methode | URL                          | Description                    |
|---------|------------------------------|--------------------------------|
| POST    | /api/ai/extract              | Lancer l'extraction (interne)  |
| GET     | /api/ai/results/{doc_id}     | Resultats d'un document        |
| GET     | /api/ai/history/{user_id}    | Historique des analyses        |
| GET     | /api/ai/model-info           | Etat du modele                 |
| GET     | /api/ai/health               | Etat du service                |

### Calcul du statut (exemple)
`Glycemie : 1.15 g/L` avec normes `0.70 - 1.10` -> **HIGH** (1.15 > 1.10).

## Chatbot Service (port 8085)

### Pipeline RAG
1. Recuperer les analyses du patient (contexte personnel) en base.
2. Chercher dans la base de connaissances medicales integree.
3. Construire un prompt structure (systeme + contextes + question).
4. Appeler **Mistral via Ollama** (`/api/generate`).
5. Filtrer la sortie (mots interdits neutralises).
6. Ajouter systematiquement le **disclaimer medical**.

### Garde-fous
- Mots interdits neutralises : `diagnostic, vous avez, prenez, medicament, posologie...`
- Question de type diagnostic -> **refus** + orientation medecin.
- Jamais de traitement ni de dose.
- Disclaimer present dans **chaque** reponse.

### Base de connaissances
Glycemie, Cholesterol (HDL/LDL/triglycerides), Hemoglobine, Vitamine D, TSH,
Creatinine/Uree.

### Endpoints
| Methode | URL                             | Description                 |
|---------|---------------------------------|-----------------------------|
| POST    | /api/chat/message               | Envoyer un message          |
| GET     | /api/chat/history               | Historique                  |
| DELETE  | /api/chat/history/{session_id}  | Effacer une session         |
| GET     | /api/chat/health                | Etat du service             |

### Installer Ollama + Mistral (local, gratuit)
```bash
# https://ollama.com
ollama pull mistral
ollama serve            # ecoute sur http://localhost:11434
```
Dans Docker, le service contacte `host.docker.internal:11434`. Si Ollama est
indisponible, le chatbot repond a partir de la base de connaissances seule.
