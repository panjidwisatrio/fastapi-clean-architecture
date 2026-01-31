from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from app.schemas.permission import Permission

# Role schemas
class RoleBase(BaseModel):
    role_name: str

class RoleCreate(RoleBase):
    pass

class RoleUpdate(RoleBase):
    pass

class PermissionRole(BaseModel):
    role_id: int
    permission_ids: List[int]

class Role(RoleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    permissions: List[Permission] = []

    class Config:
        orm_mode = True