from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List

from app.core.security import get_current_user
from app.schemas.user import User, UserCreate, UserRegister, UserUpdate
from app.schemas.token import Token
from app.api.dependencies import get_user_service, get_current_admin_user, get_pagination_params
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, service: UserService = Depends(get_user_service)):
    return service.create_user(user)

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(user: UserRegister, service: UserService = Depends(get_user_service)):
    return service.create_user(user)

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service)
):
    user = service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = service.create_access_token(user)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=User)
async def update_user_me(
    user: UserUpdate,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    return service.update_user(current_user.id, user)

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_me(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    service.delete_user(current_user.id)
    return None

@router.get("/", response_model=List[User])
async def read_users(
    skip_limit: tuple = Depends(get_pagination_params),
    service: UserService = Depends(get_user_service),
    _: User = Depends(get_current_admin_user)
):
    skip, limit = skip_limit
    return service.get_users(skip, limit)
