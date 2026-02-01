from datetime import datetime
from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel, EmailStr

if TYPE_CHECKING:
    from app.schemas.role import Role

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserSimple(UserBase):
    """Simplified user schema without role to avoid circular imports"""
    id: int
    role_id: Optional[int] = None
    is_verified: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        orm_mode = True

class UserCreate(UserBase):
    role_id: Optional[int] = None

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roles_id: Optional[int] = None
    is_verified: Optional[bool] = None
    is_active: Optional[bool] = None

class MeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    
class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str
    password_confirm: str

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
    role: Optional["Role"] = None
    
# Update forward references after all models are defined
def update_schemas():
    """Call this after all schemas are imported"""
    from app.schemas.role import Role
    User.update_forward_refs(Role=Role)