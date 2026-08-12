"""Verification locale du JWT (meme secret que l'Auth Service - DEV 1)."""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

class CurrentUser:
    def __init__(self, user_id: str, username: str, role: str):
        self.id = user_id
        self.username = username
        self.role = role

def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    exc = HTTPException(status.HTTP_401_UNAUTHORIZED, "Token invalide ou expire",
                        headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY,
                             algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise exc
    if not payload.get("sub"):
        raise exc
    return CurrentUser(payload["sub"], payload.get("username", ""), payload.get("role", "PATIENT"))
