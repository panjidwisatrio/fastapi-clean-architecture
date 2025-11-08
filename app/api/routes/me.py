from fastapi import APIRouter, Depends, status

from app.core.security import get_current_user
from app.schemas.user import PasswordUpdate, User, UserUpdate
from app.api.dependencies import get_user_service
from app.services.user_service import UserService

router = APIRouter(prefix="/me", tags=["me"])

@router.get("/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/", response_model=User)
async def update_user_me(
    user: UserUpdate,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    return service.update_user(current_user.id, user)

@router.put("/password", response_model=User)
async def update_user_password_me(
    password_update: PasswordUpdate,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    return service.update_user(current_user.id, password_update)

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user_me(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    service.deactivate_user(current_user.id)
    return None