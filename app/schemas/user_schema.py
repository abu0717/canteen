from pydantic import BaseModel, EmailStr
from enum import Enum


class UserRole(str, Enum):
    student = 'student'
    cafe_owner = 'cafe_owner'
    cafe_worker = 'cafe_worker'
    admin = 'admin'


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.student


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: UserRole

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
