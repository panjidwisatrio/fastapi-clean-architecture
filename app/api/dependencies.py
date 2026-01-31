from fastapi import Depends, Security
from sqlalchemy.orm import Session
from typing import Tuple

from app.core.database import get_db
from app.core.security import get_current_user
from app.repositories.token_blacklist_repository import TokenBlacklistRepository
from app.repositories.user_repository import UserRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.permission_repository import PermissionRepository
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.services.otp_service import OTPService
from app.services.token_blacklist_service import TokenBlacklistService
from app.services.user_service import UserService
from app.services.role_service import RoleService
from app.services.permission_service import PermissionService
from app.schemas.user import User

# Service factory dependencies
def get_email_service() -> EmailService:
    """Returns an EmailService instance with its required configuration"""
    return EmailService()

def get_user_service(db: Session = Depends(get_db), email_service: EmailService = Depends(get_email_service)) -> UserService:
    """Returns a UserService instance with its required repository"""
    return UserService(UserRepository(db), email_service=email_service)

def get_otp_service(
    db: Session = Depends(get_db), 
    user_service: UserService = Depends(get_user_service), 
    email_service: EmailService = Depends(get_email_service)
) -> OTPService:
    """Returns an OTPService instance with its required repository"""
    return OTPService(db, user_service=user_service, email_service=email_service)

def get_token_blacklist_service(db: Session = Depends(get_db)) -> TokenBlacklistService:
    """Returns a TokenBlacklistService instance with its required repository"""
    return TokenBlacklistService(db=db)

def get_auth_service(
    db: Session = Depends(get_db),
    email_service: EmailService = Depends(get_email_service),
) -> AuthService:
    """Returns an AuthService instance with its required repositories"""
    return AuthService(db=db, email_service=email_service)

def get_role_service(db: Session = Depends(get_db)) -> RoleService:
    """Returns a RoleService instance with its required repositories"""
    return RoleService(RoleRepository(db), PermissionRepository(db))

def get_permission_service(db: Session = Depends(get_db)) -> PermissionService:
    """Returns a PermissionService instance with its required repository"""
    return PermissionService(PermissionRepository(db))

# Pagination dependencies
def get_pagination_params(skip: int = 0, limit: int = 100) -> Tuple[int, int]:
    """Returns standardized pagination parameters"""
    return skip, limit
