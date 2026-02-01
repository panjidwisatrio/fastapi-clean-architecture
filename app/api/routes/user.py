from typing import List
from fastapi import APIRouter, Depends, Response, status

from app.core.cache import cache_user
from app.core.security import get_current_user_with_permission
from app.schemas.user import User, UserCreate, UserUpdate
from app.api.dependencies import get_user_service, get_pagination_params
from app.services.user_service import UserService
from app.core.config import settings

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate, 
    service: UserService = Depends(get_user_service),
    _: User = Depends(get_current_user_with_permission("create_user"))
):
    return await service.create_user(user)

@router.get("/{user_id}", response_model=User)
@cache_user(expire=settings.CACHE_EXPIRE_SECONDS)
async def read_user(
    response: Response,
    user_id: int, 
    service: UserService = Depends(get_user_service),
    _: User = Depends(get_current_user_with_permission("get_user_by_id"))
):
    # Disable browser cache - force server revalidation
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return service.get_user(user_id)

@router.put("/{user_id}", response_model=User)
async def update_user(
    user: UserUpdate,
    user_id: int,
    service: UserService = Depends(get_user_service),
    _: User = Depends(get_current_user_with_permission("update_user"))
):
    return await service.update_user(user, user_id=user_id)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
    _: User = Depends(get_current_user_with_permission("deactivate_user"))
):
    await service.deactivate_user(user_id)
    return None

@router.get("/", response_model=List[User])
@cache_user(expire=settings.CACHE_EXPIRE_SECONDS)
async def read_users(
    response: Response,
    skip_limit: tuple = Depends(get_pagination_params),
    service: UserService = Depends(get_user_service),
    _: User = Depends(get_current_user_with_permission("get_users"))
):
    # Disable browser cache - force server revalidation
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    skip, limit = skip_limit
    return service.get_users(skip, limit)
