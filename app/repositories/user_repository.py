from datetime import datetime
from typing import Union
from sqlalchemy.orm import Session
from app.core.logging import setup_logger, log_operation
from app.models.user import User
from app.schemas.user import UserCreate, UserRegister, UserUpdate
from app.core.utils import get_password_hash

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
    def get_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.db.query(User).offset(skip).limit(limit).all()

    @log_operation(logger)
    def create_user(self, user: Union[UserCreate, UserRegister]) -> User:
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            hashed_password=hashed_password,
            first_name=user.first_name,
            last_name=user.last_name,
            role_id=user.roles_id if hasattr(user, "roles_id") else 3,
            is_verified=False,
            is_active=True,
            last_active=datetime.now(datetime.timezone.utc)
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    @log_operation(logger)
    def update_user(self, user_id: int, user: UserUpdate) -> User:
        db_user = self.get_user(user_id)
        if db_user:
            update_data = user.dict(exclude_unset=True)
            if "password" in update_data:
                update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
            
            for field, value in update_data.items():
                setattr(db_user, field, value)
                
            # Update last active timestamp
            db_user.last_active = datetime.now(datetime.timezone.utc)
            self.db.commit()
            self.db.refresh(db_user)
        return db_user

    @log_operation(logger)
    def delete_user(self, user_id: int) -> User:
        db_user = self.get_user(user_id)
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
        return db_user
        
    @log_operation(logger)
    def update_last_active(self, user_id: int) -> User:
        db_user = self.get_user(user_id)
        if db_user:
            db_user.last_active = datetime.now(datetime.timezone.utc)
            self.db.commit()
            self.db.refresh(db_user)
        return db_user
