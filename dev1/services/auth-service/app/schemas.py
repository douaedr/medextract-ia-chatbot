from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=6, max_length=128)
    full_name: Optional[str] = None
    role: str = "PATIENT"   # PATIENT / DOCTOR / ADMIN

class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6, max_length=128)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int          # secondes
    user: UserOut

class TokenPayload(BaseModel):
    sub: str                 # user_id
    username: str
    role: str
