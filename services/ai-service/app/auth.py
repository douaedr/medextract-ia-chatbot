from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    exc = HTTPException(status.HTTP_401_UNAUTHORIZED, "Token invalide")
    if not token:
        raise exc
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY,
                             algorithms=[settings.JWT_ALGORITHM])
        return payload["sub"]
    except (JWTError, KeyError):
        raise exc
