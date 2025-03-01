from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# Permission schemas
class PermissionBase(BaseModel):
    permission_name: str

class PermissionCreate(PermissionBase):
    pass

class Permission(PermissionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True