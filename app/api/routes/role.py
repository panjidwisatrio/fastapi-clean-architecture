from fastapi import APIRouter, Depends, status
from typing import List

from app.schemas.role import Role, RoleCreate
from app.services.role_service import RoleService
from app.api.dependencies import (
    get_role_service,
    get_pagination_params,
    get_current_user_with_permission
)

router = APIRouter(prefix="/roles", tags=["roles"])

@router.post("/", response_model=Role, status_code=status.HTTP_201_CREATED)
async def create_role(
    role: RoleCreate, 
    service: RoleService = Depends(get_role_service),
    _: dict = Depends(get_current_user_with_permission("manage_roles"))
):
    return service.create_role(role)

@router.get("/", response_model=List[Role])
async def read_roles(
    skip_limit: tuple = Depends(get_pagination_params), 
    service: RoleService = Depends(get_role_service),
    _: dict = Depends(get_current_user_with_permission("view_roles"))
):
    skip, limit = skip_limit
    return service.get_roles(skip, limit)

@router.get("/{role_id}", response_model=Role)
async def read_role(
    role_id: int, 
    service: RoleService = Depends(get_role_service),
    _: dict = Depends(get_current_user_with_permission("view_roles"))
):
    return service.get_role(role_id)

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int, 
    service: RoleService = Depends(get_role_service),
    _: dict = Depends(get_current_user_with_permission("manage_roles"))
):
    service.delete_role(role_id)
    return None

@router.post("/{role_id}/permissions/{permission_id}", response_model=Role)
async def add_permission_to_role(
    role_id: int,
    permission_id: int,
    service: RoleService = Depends(get_role_service),
    _: dict = Depends(get_current_user_with_permission("manage_roles"))
):
    return service.add_permission_to_role(role_id, permission_id)

@router.delete("/{role_id}/permissions/{permission_id}", response_model=Role)
async def remove_permission_from_role(
    role_id: int,
    permission_id: int,
    service: RoleService = Depends(get_role_service),
    _: dict = Depends(get_current_user_with_permission("manage_roles"))
):
    return service.remove_permission_from_role(role_id, permission_id)