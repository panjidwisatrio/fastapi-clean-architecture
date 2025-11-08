from typing import Optional, Union
from fastapi import HTTPException, status
from app.core.logging import setup_logger, log_operation
from app.repositories.user_repository import UserRepository
from app.schemas.user import PasswordUpdate, UserCreate, UserUpdate, User
from app.models.user import User as UserModel
from app.schemas.auth import UserRegister
from app.core.utils import get_password_hash
from app.services.email_service import EmailService

logger = setup_logger("user_services")

class UserService:
    def __init__(self, user_repository: UserRepository, email_service: EmailService):
        self.user_repository = user_repository
        self.email_service = email_service

    @log_operation(logger)
    async def create_user(self, user: Union[UserCreate, UserRegister]) -> User:
        """
        Create a new user with validation and send welcome email if applicable
        
        Business Logic:
        1. Enforce email domain restrictions.
        2. For UserRegister:
            - Enforce password complexity.
            - Ensure password and password_confirm match.
        3. Check if email already exists.
        4. For UserCreate:
            - Validate role assignment if provided.
            - Generate a random password.
            - Hash the generated password.
            - Create user in the database.
            - Send welcome email with generated password.
        5. For UserRegister:
            - Create user in the database.
        
        Args:
            user (Union[UserCreate, UserRegister]): User creation data
            
        Returns:
            User: Created user object
            
        Raises:
            HTTPException: Email domain not allowed
            HTTPException: Password does not meet complexity requirements
            HTTPException: Password and password confirmation do not match
            HTTPException: Email already registered
            HTTPException: Invalid role assignment
            HTTPException: Failed to send welcome email, user created without email notification, please contact admin

        """
        # Business logic 1: enforce email domain restrictions
        if not UserModel.validate_email_domain(user.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email domain not allowed"
            )
        
        # Business logic 2: additional checks for UserRegister
        if user.__class__ == UserRegister:
            # Business logic 2.1: enforce password complexity for registration (enforce password complexity (at least 8 characters, one uppercase, one digit)
            if not UserModel.validate_password_complexity(user.password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password does not meet complexity requirements"
                )
                
            # Business logic 2.2: ensure password and password_confirm match for registration
            if user.password != user.password_confirm:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password and password confirmation do not match"
                )
            
        # Business logic 3: check if email already exists
        existing_user = self.user_repository.get_user_by_email(user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Business logic 4: additional checks for UserCreate
        if user.__class__ == UserCreate:
            # Business logic 4.1: validate role assignment if provided
            if hasattr(user, "roles_id") and user.roles_id is not None:
                if not self.validate_role_assignment(user.roles_id):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid role assignment"
                    )
                    
            # Business logic 4.2: generate a random password
            generated_password = UserModel.generate_random_password()
            
            # Business logic 4.3: hash the generated password
            user_dict = user.dict(exclude_unset=True)
            user_dict["hashed_password"] = get_password_hash(generated_password)

            # Business logic 4.3: create user in the database
            user = self.user_repository.create_user_with_dict(user_dict)

            # Business logic 4.4: send welcome email with generated password
            email_sent = await self.email_service.send_welcome_email(
                to_email=user.email,
                full_name=f"{user.first_name} {user.last_name}",
                generated_password=generated_password
            )
            if not email_sent:
                logger.warning(f"Failed to send welcome email to {user.email}")
                # You might want to raise an exception here
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to send welcome email, user created without email notification, please contact admin"
                )

            return user
        else:
            # Business logic 5: create user in the database for UserRegister
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
    def get_user_by_email(self, email: str) -> User:
        user = self.user_repository.get_user_by_email(email)
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
    async def update_user(self, user: Union[UserUpdate, PasswordUpdate], user_id: Optional[int] = None, email: Optional[str] = None) -> User:
        """
        Update user information with validation and send notification email if applicable
        
        Business Logic:
        1. For email update:
            - Enforce email domain restrictions.
            - Check if new email already exists.
        2. For role update:
            - Validate role assignment if provided.
        4. For PasswordUpdate:
            - Ensure old password matches current password.
            - Enforce password complexity.
            - Ensure new password and password_confirm match.
            - Hash the new password.
        5. Update the user in the database.
        6. If email was changed, send notification email.
        
        Args:
            user (Union[UserUpdate, PasswordUpdate]): User update data
            user_id (Optional[int]): ID of the user to update
            email (Optional[str]): Email of the user to update
        
        Returns:
            User: Updated user object
            
        Raises:
            HTTPException: Email domain not allowed
            HTTPException: Email already registered
            HTTPException: Invalid role assignment
            HTTPException: Old password is incorrect
            HTTPException: Password does not meet complexity requirements
            HTTPException: New password and password confirmation do not match
            HTTPException: User not found
            HTTPException: Failed to send email change notification, please contact admin
        """
        # Business logic 1: Additional checks for email update
        if hasattr(user, "email") and user.email is not None:
            # Business logic 1.1: enforce email domain restrictions if email is being updated
            if not UserModel.validate_email_domain(user.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email domain not allowed"
                )
            
            # Business logic 1.2: check if new email already exists
            existing_user = self.user_repository.get_user_by_email(user.email)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

        # Business logic 2: validate role assignment if provided
        if hasattr(user, "roles_id") and user.roles_id is not None:
            if not self.validate_role_assignment(user.roles_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid role assignment"
                )

        # Business logic 4: specific checks for PasswordUpdate
        if user.__class__ == PasswordUpdate:
            # Business logic 4.1: ensure old password matches current password
            db_user = self.get_user(user_id) if user_id else self.get_user_by_email(email)
            if not db_user or not User.verify_password(user.old_password, db_user.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Old password is incorrect"
                )
                
            # Business logic 4.2: Additional checks for password update
            if not UserModel.validate_password_complexity(user.new_password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password does not meet complexity requirements"
                )
            
            # Business logic 4.3: ensure new password and password_confirm match
            if user.new_password != user.password_confirm:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="New password and password confirmation do not match"
                )
                
            # Business logic 4.4: Hash the new password
            user = UserUpdate(hashed_password=get_password_hash(user.new_password))
        
        # Update the user
        db_user = self.user_repository.update_user(user, user_id=user_id, email=email)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        #  Business logic 5: send notification email if email was changed
        if hasattr(user, "email") and user.email is not None:
            email_sent = await self.email_service.send_email_change_notification(
                to_email=user.email,
                full_name=f"{db_user.first_name} {db_user.last_name}"
            )
            if not email_sent:
                logger.warning(f"Failed to send email change notification to {user.email}")
                # You might want to raise an exception here
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to send email change notification, please contact admin"
                )
        
        return db_user

    @log_operation(logger)
    def deactivate_user(self, user_id: int) -> User:
        db_user = self.user_repository.deactivate_user(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return db_user
    
    @log_operation(logger)
    def check_user_permission(self, user_id: int, permission_name: str) -> bool:
        user = self.user_repository.get_user(user_id)
        if not user or not user.role:
            return False
        
        for permission in user.role.permissions:
            if permission.permission_name == permission_name:
                return True
                
        return False
    
    @log_operation(logger)
    def is_user_active(self, user_id: int = None, email: str = None) -> bool:
        """Check if the user is active by user ID or email."""
        if user_id is not None:
            user = self.user_repository.get_user(user_id)
        elif email is not None:
            user = self.user_repository.get_user_by_email(email)
        else:
            raise ValueError("Either user_id or email must be provided")

        return user.is_active if user else False

    @log_operation(logger)
    def is_user_verified(self, user_id: int = None, email: str = None) -> bool:
        """Check if the user is verified by user ID or email."""
        if user_id is not None:
            user = self.user_repository.get_user(user_id)
        elif email is not None:
            user = self.user_repository.get_user_by_email(email)
        else:
            raise ValueError("Either user_id or email must be provided")
        
        return user.is_verified if user else False
    
    @log_operation(logger)
    def validate_role_assignment(self, role_id: int) -> bool:
        from app.models.role import Role
        role = self.user_repository.db.query(Role).filter(Role.id == role_id).first()
        return role is not None