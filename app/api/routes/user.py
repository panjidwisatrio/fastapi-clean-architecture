from typing import List
from fastapi import APIRouter, Depends, status

from app.schemas.user import User, UserCreate, UserUpdate
from app.api.dependencies import get_current_user_with_permission, get_user_service, get_pagination_params
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate, 
    service: UserService = Depends(get_user_service),
    _: User = Depends(get_current_user_with_permission("create_user"))
):
    return await service.create_user(user)

@router.get("/{user_id}", response_model=User)
async def read_user(
    user_id: int, 
    service: UserService = Depends(get_user_service),
    _: User = Depends(get_current_user_with_permission("get_user_info_by_id"))
):
    return service.get_user(user_id)

@router.put("/{user_id}", response_model=User)
async def update_user(
    user: UserUpdate,
    user_id: int,
    service: UserService = Depends(get_user_service),
    _: User = Depends(get_current_user_with_permission("update_user_info"))
):
    return service.update_user(user, user_id=user_id)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
    _: User = Depends(get_current_user_with_permission("update_user_active_status"))
):
    service.deactivate_user(user_id)
    return None

@router.get("/", response_model=List[User])
async def read_users(
    skip_limit: tuple = Depends(get_pagination_params),
    service: UserService = Depends(get_user_service),
    _: User = Depends(get_current_user_with_permission("get_all_users_info"))
):
    skip, limit = skip_limit
    return service.get_users(skip, limit)
