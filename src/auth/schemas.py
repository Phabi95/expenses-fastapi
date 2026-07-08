from datetime import datetime

from pydantic import BaseModel, EmailStr

from src.auth.models import Role


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenUser(BaseModel):
    id: int
    role: Role


class CreatePassword(BaseModel):
    token: str
    new_password: str
