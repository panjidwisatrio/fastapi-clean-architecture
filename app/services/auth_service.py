from typing import Optional
from fastapi import HTTPException, status
from app.core.logging import setup_logger, log_operation
from app.schemas.user import User, UserUpdate
from app.schemas.auth import UserRegister
from app.core.security import create_access_token
from app.core.utils import get_current_utc_time, verify_password
from app.services.email_service import EmailService
from app.services.otp_service import OTPService
from app.models.otp import OTPType
from app.services.token_blacklist_service import TokenBlacklistService
from app.services.user_service import UserService

logger = setup_logger("auth_services")

class AuthService:
    def __init__(
        self, 
        user_service: UserService, 
        email_service: EmailService, 
        otp_service: OTPService,
        blacklist_service: TokenBlacklistService
    ):
        self.user_service = user_service
        self.email_service = email_service
        self.otp_service = otp_service
        self.blacklist_service = blacklist_service

    @log_operation(logger)
    def create_access_token(self, user: User) -> str:
        return create_access_token({"sub": user.id})
    
    @log_operation(logger)
    async def register_user(self, user: UserRegister) -> User:
        try:
            user = await self.user_service.create_user(user)
            return user
        except HTTPException as http_exc:
            logger.error(f"HTTP error in register_user for email {user.email}: {http_exc.detail}")
            raise
        except Exception as e:
            logger.error(f"Error in register_user for email {user.email}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to register user"
            )
    
    @log_operation(logger)
    def authenticate_user(self, email: str, password: str) -> User:
        # Business logic 1: check if user exists
        try:
            user = self.user_service.get_user_by_email(email)
        except HTTPException as http_exc:
            logger.error(f"HTTP error in authenticate_user for email {email}: {http_exc.detail}")
            raise
        except Exception as e:
            logger.error(f"Error in authenticate_user for email {email}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to authenticate user"
            )

        # Business logic 2: verify password
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password"
            )
        
        # Update last active timestamp
        self.user_service.update_user(UserUpdate(last_active=get_current_utc_time()), user_id=user.id)
        return user
    
    @log_operation(logger)
    def logout_user(self, user: User, token: Optional[str] = None) -> None:
        # Business logic 1: update last active timestamp
        self.user_service.update_user(UserUpdate(last_active=get_current_utc_time()), user_id=user.id)
        
        # Business logic 2: blacklist token if provided
        if token:
            self.blacklist_service.blacklist_token(token)
        
        return
    
    @log_operation(logger)
    async def forgot_password(self, email: str) -> dict:
        """
        Generate OTP and send reset password email
        
        Args:
            email (str): User's email address
            
        Returns:
            dict: Information about the sent OTP
        """
        try:
            # Create new OTP and send email
            _ = await self.otp_service.create_otp_and_send(
                email=email,
                type=OTPType.RESET_PASSWORD
            )
            
            return {"message": "Password reset OTP sent to email"}
        except HTTPException as http_exc:
            logger.error(f"HTTP error in forgot_password for email {email}: {http_exc.detail}")
            raise
        except Exception as e:
            logger.error(f"Error in forgot_password for email {email}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process forgot password request"
            )
