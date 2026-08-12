from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError

from ..database import get_db
from ..models import User
from ..schemas import (UserRegister, UserOut, UserUpdate, PasswordChange, Token)
from ..security import (hash_password, verify_password, create_access_token, decode_token)
from ..deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

VALID_ROLES = {"PATIENT", "DOCTOR", "ADMIN"}


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if data.role not in VALID_ROLES:
        raise HTTPException(400, "Role invalide (PATIENT / DOCTOR / ADMIN)")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Email deja utilise")
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(400, "Nom d'utilisateur deja utilise")

    user = User(
        email=data.email,
        username=data.username,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/token", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # form.username peut etre l'email OU le username
    user = (db.query(User)
              .filter((User.email == form.username) | (User.username == form.username))
              .first())
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Identifiants incorrects")
    if not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Compte desactive")

    token, expires_in = create_access_token(user.id, user.username, user.role)
    return Token(access_token=token, expires_in=expires_in, user=user)


@router.get("/me", response_model=UserOut)
def read_me(current: User = Depends(get_current_user)):
    return current


@router.put("/me", response_model=UserOut)
def update_me(data: UserUpdate,
              current: User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    if data.email and data.email != current.email:
        if db.query(User).filter(User.email == data.email).first():
            raise HTTPException(400, "Email deja utilise")
        current.email = data.email
    if data.full_name is not None:
        current.full_name = data.full_name
    db.commit()
    db.refresh(current)
    return current


@router.post("/change-password")
def change_password(data: PasswordChange,
                    current: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    if not verify_password(data.old_password, current.hashed_password):
        raise HTTPException(400, "Ancien mot de passe incorrect")
    current.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"message": "Mot de passe modifie avec succes"}


@router.get("/verify-token")
def verify_token(token: str, db: Session = Depends(get_db)):
    """Utilise par les autres microservices pour valider un JWT."""
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token invalide ou expire")
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Utilisateur introuvable")
    return {"valid": True, "user_id": str(user.id),
            "username": user.username, "role": user.role}


@router.get("/health")
def health():
    return {"status": "ok", "service": "auth-service"}
