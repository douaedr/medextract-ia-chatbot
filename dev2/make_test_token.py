"""Genere un JWT de test pour appeler Document/OCR sans lancer l'Auth Service.
Usage : python make_test_token.py <user_id_uuid>
Le user_id doit exister dans la table users (ex : le compte admin de demo)."""
import sys
from datetime import datetime, timedelta, timezone
from jose import jwt

SECRET = "dev-secret-change-me"   # doit correspondre a JWT_SECRET_KEY

user_id = sys.argv[1] if len(sys.argv) > 1 else "00000000-0000-0000-0000-000000000000"
payload = {
    "sub": user_id,
    "username": "tester",
    "role": "PATIENT",
    "exp": datetime.now(timezone.utc) + timedelta(hours=24),
}
print(jwt.encode(payload, SECRET, algorithm="HS256"))
