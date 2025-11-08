from datetime import datetime, timezone
from typing import Optional, Union
from sqlalchemy.orm import Session
from app.core.logging import setup_logger, log_operation
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.auth import UserRegister
from app.core.utils import get_current_utc_time, get_password_hash

logger = setup_logger("user_repositories")

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    @log_operation(logger)
    def get_user(self, user_id: int) -> User:
        return self.db.query(User).filter(User.id == user_id).first()

    @log_operation(logger)
    def get_user_by_email(self, email: str) -> User:
        return self.db.query(User).filter(User.email == email).first()

    @log_operation(logger)
    def get_users(self, skip: int = 0, limit: int = 100, exclude_super_admin: bool = True) -> list[User]:
        query = self.db.query(User)
        if exclude_super_admin:
            query = query.filter(User.role_id != 1)  # Exclude super admin users
        return query.offset(skip).limit(limit).all()

    @log_operation(logger)
    def create_user(self, user: Union[UserCreate, UserRegister]) -> User:
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            hashed_password=hashed_password,
            first_name=user.first_name,
            last_name=user.last_name,
            role_id=user.role_id if hasattr(user, "role_id") and user.role_id else 3,
            is_verified=False,
            is_active=True,
            last_active=get_current_utc_time()
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    @log_operation(logger)
    def create_user_with_dict(self, user_data: dict) -> User:
        """Create user from dictionary data (for cases where we need to add hashed_password)"""
        db_user = User(**user_data)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    @log_operation(logger)
    def update_user(self, user: UserUpdate, user_id: Optional[int] = None, email: Optional[str] = None) -> User:
        db_user = self.get_user(user_id) if user_id else self.get_user_by_email(email)
        if db_user:
            update_data = user.dict(exclude_unset=True)
            if "password" in update_data:
                update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
            
            for field, value in update_data.items():
                setattr(db_user, field, value)
                
            # Update last active timestamp
            db_user.last_active = get_current_utc_time()
            self.db.commit()
            self.db.refresh(db_user)
        return db_user

    @log_operation(logger)
    def deactivate_user(self, user_id: int) -> User:
        db_user = self.get_user(user_id)
        if db_user:
            self.db.query(User).filter(User.id == user_id).update({"is_active": False})
            self.db.commit()
        return db_user
        
    @log_operation(logger)
    def update_last_active(self, user_id: int) -> User:
        db_user = self.get_user(user_id)
        if db_user:
            db_user.last_active = get_current_utc_time()
            self.db.commit()
            self.db.refresh(db_user)
        return db_user