from fastapi import APIRouter, Depends, Response, status
from typing import List

from app.core.security import get_current_user_with_permission
from app.schemas.role import PermissionRole, Role, RoleCreate, RoleUpdate
from app.services.role_service import RoleService
from app.api.dependencies import (
    get_role_service,
    get_pagination_params,
)
from app.core.cache import cache_role
from app.core.config import settings

router = APIRouter(prefix="/roles", tags=["roles"])

@router.post("/", response_model=Role, status_code=status.HTTP_201_CREATED)
async def create_role(
    role: RoleCreate, 
    service: RoleService = Depends(get_role_service),
    _: dict = Depends(get_current_user_with_permission("manage_roles"))
):
    return await service.create_role(role)

@router.put("/{role_id}", response_model=Role)
async def update_role(
    role_id: int,
    role: RoleUpdate,
    service: RoleService = Depends(get_role_service),
    _: dict = Depends(get_current_user_with_permission("manage_roles"))
):
    return await service.update_role(role_id, role)

@router.get("/", response_model=List[Role])
@cache_role(expire=settings.CACHE_EXPIRE_SECONDS)
async def read_roles(
    response: Response,
    skip_limit: tuple = Depends(get_pagination_params), 
    service: RoleService = Depends(get_role_service),
    _: dict = Depends(get_current_user_with_permission("view_roles"))
):
    # Disable browser cache - force server revalidation
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    skip, limit = skip_limit
    return service.get_roles(skip, limit)

@router.get("/{role_id}", response_model=Role)
@cache_role(expire=settings.CACHE_EXPIRE_SECONDS)
async def read_role(
    response: Response,
    role_id: int, 
    service: RoleService = Depends(get_role_service),
    _: dict = Depends(get_current_user_with_permission("view_roles"))
):
    # Disable browser cache - force server revalidation
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return service.get_role(role_id)

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int, 
    service: RoleService = Depends(get_role_service),
    _: dict = Depends(get_current_user_with_permission("manage_roles"))
):
    await service.delete_role(role_id)
    return None

@router.post("/permissions", response_model=Role)
async def add_permission_to_role(
    permissions: PermissionRole,
    service: RoleService = Depends(get_role_service),
    _: dict = Depends(get_current_user_with_permission("manage_roles"))
):
    return service.add_permission_to_role(permissions)

@router.delete("/permissions", response_model=Role)
async def remove_permission_from_role(
    permissions: PermissionRole,
    service: RoleService = Depends(get_role_service),
    _: dict = Depends(get_current_user_with_permission("manage_roles"))
):
    return service.remove_permission_from_role(permissions)