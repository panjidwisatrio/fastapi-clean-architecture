from fastapi import APIRouter, Depends, status
from typing import List

from app.schemas.permission import Permission, PermissionCreate
from app.services.permission_service import PermissionService
from app.api.dependencies import (
    get_permission_service, 
    get_pagination_params,
    get_current_user_with_permission
)

router = APIRouter(prefix="/permissions", tags=["permissions"])

@router.post("/", response_model=Permission, status_code=status.HTTP_201_CREATED)
async def create_permission(
    permission: PermissionCreate, 
    service: PermissionService = Depends(get_permission_service),
    _: dict = Depends(get_current_user_with_permission("manage_permissions"))
):
    return service.create_permission(permission)

@router.get("/", response_model=List[Permission])
async def read_permissions(
    skip_limit: tuple = Depends(get_pagination_params), 
    service: PermissionService = Depends(get_permission_service),
    _: dict = Depends(get_current_user_with_permission("view_permissions"))
):
    skip, limit = skip_limit
    return service.get_permissions(skip, limit)

@router.get("/{permission_id}", response_model=Permission)
async def read_permission(
    permission_id: int, 
    service: PermissionService = Depends(get_permission_service),
    _: dict = Depends(get_current_user_with_permission("view_permissions"))
):
    return service.get_permission(permission_id)

@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    permission_id: int, 
    service: PermissionService = Depends(get_permission_service),
    _: dict = Depends(get_current_user_with_permission("manage_permissions"))
):
    service.delete_permission(permission_id)
    return None
