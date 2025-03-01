from typing import Union
from fastapi import HTTPException, status
from app.core.logging import setup_logger, log_operation
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate, User, UserRegister
from app.core.security import create_access_token
from app.core.utils import verify_password

logger = setup_logger("user_services")

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    @log_operation(logger)
    def authenticate_user(self, email: str, password: str) -> User:
        user = self.user_repository.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password"
            )
        
        # Update last active timestamp
        self.user_repository.update_last_active(user.id)
        return user

    @log_operation(logger)
    def create_user(self, user: Union[UserCreate, UserRegister]) -> User:
        existing_user = self.user_repository.get_user_by_email(user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        return self.user_repository.create_user(user)

    @log_operation(logger)
    def get_user(self, user_id: int) -> User:
        user = self.user_repository.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    @log_operation(logger)
    def get_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.user_repository.get_users(skip, limit)

    @log_operation(logger)
    def update_user(self, user_id: int, user: UserUpdate) -> User:
        db_user = self.user_repository.update_user(user_id, user)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return db_user

    @log_operation(logger)
    def delete_user(self, user_id: int) -> User:
        db_user = self.user_repository.delete_user(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return db_user

    @log_operation(logger)
    def create_access_token(self, user: User) -> str:
        return create_access_token({"sub": user.id})
        
    @log_operation(logger)
    def check_user_permission(self, user_id: int, permission_name: str) -> bool:
        user = self.user_repository.get_user(user_id)
        if not user or not user.role:
            return False
        
        for permission in user.role.permissions:
            if permission.permission_name == permission_name:
                return True
                
        return False
