from fastapi import APIRouter, Depends, Response, status

from app.core.security import get_current_user
from app.schemas.user import MeUpdate, PasswordUpdate, User, UserUpdate
from app.api.dependencies import get_user_service
from app.services.user_service import UserService
from app.core.cache import cache_user
from app.core.config import settings

router = APIRouter(prefix="/me", tags=["me"])

@router.get("/", response_model=User)
@cache_user(expire=settings.CACHE_EXPIRE_SECONDS)
async def read_users_me(
    response: Response,
    current_user: User = Depends(get_current_user)
):
    # Disable browser cache - force server revalidation
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return current_user

@router.put("/", response_model=User)
async def update_user_me(
    user: MeUpdate,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    return await service.update_user(user, current_user.id)

@router.put("/password", response_model=User)
async def update_user_password_me(
    password_update: PasswordUpdate,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    return await service.update_user(password_update, current_user.id)

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user_me(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    await service.deactivate_user(current_user.id)
    return {"message": "User deactivated successfully"}