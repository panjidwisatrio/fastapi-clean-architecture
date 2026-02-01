from fastapi import APIRouter, Depends, Response, status
from typing import List

from app.core.security import get_current_user_with_permission
from app.schemas.permission import Permission, PermissionCreate
from app.services.permission_service import PermissionService
from app.api.dependencies import (
    get_permission_service, 
    get_pagination_params
)
from app.core.cache import cache_permission
from app.core.config import settings

router = APIRouter(prefix="/permissions", tags=["permissions"])

@router.post("/", response_model=Permission, status_code=status.HTTP_201_CREATED)
async def create_permission(
    permission: PermissionCreate, 
    service: PermissionService = Depends(get_permission_service),
    _: dict = Depends(get_current_user_with_permission("manage_permissions"))
):
    return await service.create_permission(permission)

@router.get("/", response_model=List[Permission])
@cache_permission(expire=settings.CACHE_EXPIRE_SECONDS)
async def read_permissions(
    response: Response,
    skip_limit: tuple = Depends(get_pagination_params), 
    service: PermissionService = Depends(get_permission_service),
    _: dict = Depends(get_current_user_with_permission("view_permissions"))
):
    # Disable browser cache - force server revalidation
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    skip, limit = skip_limit
    return service.get_permissions(skip, limit)

@router.get("/{permission_id}", response_model=Permission)
@cache_permission(expire=settings.CACHE_EXPIRE_SECONDS)
async def read_permission(
    response: Response,
    permission_id: int, 
    service: PermissionService = Depends(get_permission_service),
    _: dict = Depends(get_current_user_with_permission("view_permissions"))
):
    # Disable browser cache - force server revalidation
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return service.get_permission(permission_id)

@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    permission_id: int, 
    service: PermissionService = Depends(get_permission_service),
    _: dict = Depends(get_current_user_with_permission("manage_permissions"))
):
    await service.delete_permission(permission_id)
    return None
