from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel

from app.schemas.permission import Permission

if TYPE_CHECKING:
    from app.schemas.user import UserSimple

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
    
class UsersRoleAssignment(BaseModel):
    role_id: int
    user_ids: List[int]  # e.g., user_id
    
class RoleSimple(RoleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class Role(RoleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    permissions: List[Permission] = []

    class Config:
        orm_mode = True
        
class RoleDetail(Role):
    """Role schema with assigned users"""
    users: List["UserSimple"] = []  # Forward reference to avoid circular import

    class Config:
        orm_mode = True

class FailedAssignment(BaseModel):
    user_id: int
    reason: str
    
class UserAssignmentResult(RoleDetail):
    failed_assignments: List[FailedAssignment] = []
    
class UserUnassignmentResult(RoleDetail):
    failed_unassignments: List[FailedAssignment] = []
        
# Update forward references after all models are defined
def update_schemas():
    """Call this after all schemas are imported"""
    from app.schemas.user import UserSimple
    RoleDetail.update_forward_refs(UserSimple=UserSimple)
    UserAssignmentResult.update_forward_refs(UserSimple=UserSimple)
    UserUnassignmentResult.update_forward_refs(UserSimple=UserSimple)