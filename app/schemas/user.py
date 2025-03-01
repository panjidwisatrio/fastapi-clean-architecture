from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr

from app.schemas.role import Role

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    roles_id: Optional[int] = None

class UserRegister(UserBase):
    password: str

class UserUpdate(BaseModel):
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roles_id: Optional[int] = None
    is_verified: Optional[bool] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    id: int
    role_id: Optional[int] = None
    is_verified: bool
    is_active: bool
    last_active: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class User(UserInDB):
    role: Optional[Role] = None
