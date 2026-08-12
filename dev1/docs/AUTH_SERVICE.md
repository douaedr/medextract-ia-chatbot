# Auth Service - Documentation (DEV 1)

## 1. Role
Le service d'authentification gere les comptes utilisateurs, la connexion,
et la generation/verification des tokens JWT utilises par TOUS les autres
microservices.

## 2. Comment fonctionne le JWT dans ce projet

1. L'utilisateur envoie `email/username + mot de passe` sur `POST /api/auth/token`.
2. Le service verifie le mot de passe (bcrypt) et genere un **JWT** signe avec
   `JWT_SECRET_KEY` (algorithme HS256), valable **24 heures**.
3. Le token contient : `sub` (id utilisateur), `username`, `role`, `exp`, `iat`.
4. Pour chaque requete protegee, le client envoie l'en-tete :
   `Authorization: Bearer <token>`.
5. Chaque microservice verifie le token de deux facons possibles :
   - **Local** (recommande) : decoder le token avec la meme `JWT_SECRET_KEY`.
   - **Distant** : appeler `GET /api/auth/verify-token?token=...`.

> La cle `JWT_SECRET_KEY` est PARTAGEE via le fichier `.env`. Tous les services
> doivent utiliser exactement la meme valeur, sinon la verification echoue.

## 3. Schema de la table `users`

| Champ            | Type         | Description                          |
|------------------|--------------|--------------------------------------|
| id               | UUID (PK)    | Identifiant unique                   |
| email            | VARCHAR      | Email unique                         |
| username         | VARCHAR      | Nom d'utilisateur unique             |
| hashed_password  | VARCHAR      | Mot de passe hashe (bcrypt)          |
| full_name        | VARCHAR      | Nom complet (optionnel)              |
| role             | VARCHAR      | PATIENT / DOCTOR / ADMIN             |
| is_active        | BOOLEAN      | Compte actif                         |
| created_at       | TIMESTAMP    | Date de creation                     |

## 4. Endpoints

| Methode | URL                          | Description                          |
|---------|------------------------------|--------------------------------------|
| POST    | /api/auth/register           | Inscription                          |
| POST    | /api/auth/token              | Connexion (retourne le JWT)          |
| GET     | /api/auth/me                 | Profil de l'utilisateur connecte     |
| PUT     | /api/auth/me                 | Modifier son profil                  |
| POST    | /api/auth/change-password    | Changer son mot de passe             |
| GET     | /api/auth/verify-token       | Verifier un JWT (autres services)    |
| GET     | /api/auth/health             | Etat du service                      |

## 5. Lancer le service SEUL (sans Docker)

```bash
cd services/auth-service
python -m venv .venv && source .venv/bin/activate    # (Windows : .venv\Scripts\activate)
pip install -r requirements.txt

# Une base PostgreSQL doit tourner. Exemple rapide :
#   docker run -e POSTGRES_USER=medextract -e POSTGRES_PASSWORD=medextract \
#     -e POSTGRES_DB=medextract -p 5432:5432 postgres:16

export DATABASE_URL="postgresql://medextract:medextract@localhost:5432/medextract"
export JWT_SECRET_KEY="dev-secret-change-me"

uvicorn app.main:app --reload --port 8081
# Swagger : http://localhost:8081/docs
```

## 6. Tests Swagger (captures a inserer dans le rapport)

1. `POST /register` avec un nouvel email -> 201 + profil JSON.
2. `POST /register` avec le meme email -> **400 Email deja utilise**.
3. `POST /token` bon mot de passe -> 200 + `access_token`.
4. `POST /token` mauvais mot de passe -> **401 Identifiants incorrects**.
5. `GET /me` sans token -> **401**. Avec token (bouton "Authorize") -> profil.

> Inserer ici les captures d'ecran Swagger.
