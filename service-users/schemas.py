from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
import uuid


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str
    roles: List[str]

    class Config:
        from_attributes = True


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str = Field(min_length=1)
    roles: Optional[List[str]] = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProfileUpdateIn(BaseModel):
    name: Optional[str] = None
    roles: Optional[List[str]] = None


class UsersPage(BaseModel):
    items: List[UserOut]
    total: int
    page: int
    size: int
