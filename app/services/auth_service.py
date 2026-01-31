from datetime import timedelta
from typing import Optional
from fastapi import HTTPException, status
from jose import JWTError
from requests import Session
from app.core.logging import setup_logger, log_operation
from app.models.token_blacklist import TokenType
from app.repositories.otp_repository import OTPRepository
from app.repositories.token_blacklist_repository import TokenBlacklistRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import PasswordUpdate, User, UserUpdate
from app.schemas.auth import ForgotPasswordRequest, ResendVerificationOTPRequest, UserRegister, VerifyEmailRequest
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.core.utils import verify_password
from app.services.email_service import EmailService
from app.models.otp import OTP, OTPType
from app.models.user import User as UserModel
from app.core.config import settings

logger = setup_logger("auth_services")

class AuthService:
    """
    Service for handling authentication and user management logic.
    
    Attributes:
        user_repository (UserRepository): Repository for user data operations.
        otp_repository (OTPRepository): Repository for OTP data operations.
        blacklist_repository (TokenBlacklistRepository): Repository for token blacklist operations.
        email_service (EmailService): Service for sending emails.
        
    Methods:
        create_access_token(user: User) -> str
        register_user(user: UserRegister) -> User
        verify_email(verify_request: VerifyEmailRequest) -> bool
        resend_verification_otp(resend_request: ResendVerificationOTPRequest) -> dict
        authenticate_user(email: str, password: str) -> User
        logout_user(user: User, token: Optional[str] = None) -> None
        forgot_password(forgot_password_request: ForgotPasswordRequest) -> dict
        verify_reset_password(token: str) -> bool
        reset_password(token: str, updated_password: PasswordUpdate) -> dict
    """
    def __init__(
        self, 
        db: Session, 
        email_service: EmailService, 
    ):
        self.user_repository = UserRepository(db)
        self.otp_repository = OTPRepository(db)
        self.blacklist_repository = TokenBlacklistRepository(db)
        
        # External services
        self.email_service = email_service
    
    @log_operation(logger)
    def refresh_access_token(self, refresh_token: str) -> str:
        try:
            payload = decode_token(refresh_token)
            user_id = payload.get("sub")
        except HTTPException:
            raise
        except JWTError as e:
            logger.error(f"Failed to decode refresh token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user = self.user_repository.get_user(user_id)
        if not user:
            logger.error(f"Failed to refresh access token, user not found for id: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return create_access_token({"sub": user.id}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    
    @log_operation(logger)
    async def register_user(self, user: UserRegister) -> User:
        """
        Register a new user with validation
        
        Business Logic:
        1. Enforce email domain restrictions.
        2. Enforce password complexity for registration (at least 8 characters, one uppercase, one digit).
        3. Ensure password and password_confirm match for registration.
        4. Check if email already exists.
        5. Create user in the database.
        6. Generate verification OTP.
        7. Save OTP to database.
        8. Send verification email.

        Args:
            user (UserRegister): User registration data

        Raises:
            HTTPException: Email domain not allowed
            HTTPException: Password does not meet complexity requirements
            HTTPException: Password and password confirmation do not match
            HTTPException: Email already registered

        Returns:
            User: Created user object
        """
        # Business logic 1: enforce email domain restrictions
        if not UserModel.validate_email_domain(user.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email domain not allowed"
            )

        # Business logic 2: enforce password complexity for registration (enforce password complexity (at least 8 characters, one uppercase, one digit)
        if not UserModel.validate_password_complexity(user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password does not meet complexity requirements"
            )
            
        # Business logic 3: ensure password and password_confirm match for registration
        if user.password != user.password_confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password and password confirmation do not match"
            )
        
        # Business logic 4: check if email already exists
        existing_user = self.user_repository.get_user_by_email(user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Business logic 5: create user in the database for UserRegister
        user = self.user_repository.create_user(user)
        
        # Business logic 6: generate verification OTP (omitted for brevity)
        otp = OTP.generate_code()
        expires_at = OTP.get_expiry_time()
        
        # Business logic 7: save OTP to database
        self.otp_repository.create(
            email=user.email,
            code=otp,
            type=OTPType.REGISTER,
            expires_at=expires_at,
            user_id=user.id
        )
        
        # Business logic 8: send verification email
        email_sent = await self.email_service.send_verification_email(
            to_email=user.email,
            otp_code=otp,
            otp_type=OTPType.REGISTER
        )
        if not email_sent:
            logger.warning(f"Failed to send otp email to {user.email}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send otp email, account created without email notification, please contact support"
            )
        
        return user
    
    @log_operation(logger)
    async def verify_email(self, verify_request: VerifyEmailRequest) -> bool:
        """
        Verify user's email using OTP
        
        Business Logic:
        1. Retrieve valid OTP from the database.
        2. Mark OTP as used.
        3. Update user's is_verified status.

        Args:
            email (str): User's email address
            code (str): OTP code

        Raises:
            HTTPException: OTP not found or already used

        Returns:
            bool: True if verification successful
        """
        # Business logic 1: retrieve valid OTP
        otp_record = self.otp_repository.get_valid_otp(verify_request.email, verify_request.otp_code, OTPType.REGISTER)
        if not otp_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="OTP not found or already used"
            )
        
        # Business logic 2: mark OTP as used
        self.otp_repository.mark_as_used(otp_record)
        
        # Business logic 3: update user's is_verified status
        self.user_repository.verify_user(verify_request.email)
        
        return True
    
    @log_operation(logger)
    async def resend_verification_otp(self, resend_request: ResendVerificationOTPRequest) -> dict:
        """
        Resend verification OTP to user's email
        
        Business Logic:
        1. Check if user exists.
        2. Check if user is already verified.
        3. Invalidate previous OTPs for email verification.
        4. Generate new OTP code and expiry time.
        5. Save OTP to database.
        6. Send OTP via email.
        
        Args:
            email (str): User's email address
            
        Returns:
            dict: Information about the sent OTP
            
        Raises:
            HTTPException: User not found
            HTTPException: User already verified
            HTTPException: Failed to generate OTP code
            HTTPException: Failed to send verification email
        """
        # Business Logic 1: Check if user exists
        user = self.user_repository.get_user_by_email(resend_request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        # Business Logic 2: Check if user is already verified
        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already verified"
            )
            
        # Business Logic 3: Invalidate previous OTPs
        self.otp_repository.invalidate_previous_otps(resend_request.email, OTPType.REGISTER)
        
        # Business Logic 4: Generate OTP
        try:
            code = OTP.generate_code()
            expires_at = OTP.get_expiry_time()
        except Exception as e:
            logger.error(f"Error generating OTP code: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate OTP code"
            )
            
        # Business Logic 5: Save to database
        otp = self.otp_repository.create(
            email=resend_request.email,
            code=code,
            type=OTPType.REGISTER,
            expires_at=expires_at,
            user_id=user.id
        )
        
        # Business Logic 6: Send OTP via email
        email_sent = await self.email_service.send_verification_email(
            to_email=resend_request.email,
            otp_code=code,
            otp_type=OTPType.REGISTER
        )
        if not email_sent:
            logger.error(f"Failed to send verification email to {resend_request.email}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email"
            )
            
        return otp
    
    @log_operation(logger)
    def authenticate_user(self, email: str, password: str) -> User:
        """
        Authenticate a user by email and password
        
        Business Logic:
        1. Check if user exists.
        2. Verify the provided password against the stored hashed password.
        3. Update last active timestamp upon successful authentication.
        4. Generate access and refresh tokens.
        
        Args:
            email (str): User's email address
            password (str): User's password
        
        Raises:
            HTTPException: User not found
            HTTPException: Incorrect password

        Returns:
            User: Authenticated user object
        """
        # Business logic 1: check if user exists
        user = self.user_repository.get_user_by_email(email)
        if not user:
            logger.warning(f"Authentication failed, user not found for email: {email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Business logic 2: verify password
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed, incorrect password for email: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password"
            )
        
        # Business Logic 3: Update last active timestamp
        self.user_repository.update_last_active(email=user.email)
        
        # Business logic 4: Generate Access and Refresh Tokens
        access_token, expires_in = create_access_token({"sub": user.id}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        refresh_token, max_age = create_refresh_token({"sub": user.id}, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
        
        return access_token, refresh_token, expires_in, max_age
    
    @log_operation(logger)
    def logout_user(self, user: User, token: Optional[str] = None) -> None:
        """
        Logout user by blacklisting the provided token and updating last active timestamp

        Business Logic:
        1. Update user's last active timestamp.
        2. Blacklist the provided token if present.
        
        Args:
            user (User): User object
            token (Optional[str], optional): JWT token to blacklist. Defaults to None.

        Raises:
            HTTPException: Raised when token decoding fails or token is invalid.
        """
        # Business logic 1: update last active timestamp
        self.user_repository.update_last_active(user_id=user.id)
        
        try:
            # Business logic 2: blacklist token if provided
            if token:
                # Business logic 2.1: decode token to get expiration
                payload = decode_token(token)
                expires_at = payload.get("exp")
                
                # Business Logic 2.2: Check if token is already blacklisted
                if self.token_blacklist_repository.is_blacklisted(token):
                    logger.warning(f"Token already blacklisted")
                    return
                
                # Business Logic 2.3: Add to blacklist
                self.token_blacklist_repository.add_to_blacklist(token, expires_at, token_type=TokenType.ACCESS)
                logger.info(f"Token successfully blacklisted, expires at {expires_at}")
            
            return
        except HTTPException:
            raise
        except JWTError as e:
            logger.error(f"Failed to decode token during logout: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )
    
    @log_operation(logger)
    async def forgot_password(self, forgot_password_request: ForgotPasswordRequest) -> dict:
        """
        Generate token and send reset password email
        
        Business Logic:
        1. Check if user exists.
        2. Check if user is verified.
        4. Generate access token for password reset.
        6. Send token via email.
        
        Args:
            email (str): User's email address
            
        Returns:
            dict: Information about the sent token
            
        Raises:
            HTTPException: User not found
            HTTPException: User email is not verified
            HTTPException: Failed to send reset password email
        """
        # Business Logic 1: Check if user exists
        user = self.user_repository.get_user_by_email(forgot_password_request.email)
        if not user:
            logger.error(f"Forgot password requested for non-existent email: {forgot_password_request.email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        # Business Logic 2: Check if user is verified
        if not user.is_verified:
            logger.error(f"Forgot password requested for unverified email: {forgot_password_request.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User email is not verified"
            )
        
        # Business Logic 4: Generate access token
        token, expires_in = create_access_token(
            {"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_RESET_PASSWORD_EXPIRE_MINUTES)
        )
        
        # Business Logic 6: Send token via email
        email_sent = await self.email_service.send_reset_password_email(
            to_email=forgot_password_request.email,
            token=token
        )
        if not email_sent:
            logger.error(f"Failed to send reset password email to {forgot_password_request.email}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send reset password email"
            )
            
        return {"message": "Reset password email sent", "expires_in": expires_in}
    
    @log_operation(logger)
    async def verify_reset_password(self, token: str) -> bool:
        """
        Verify reset password token

        Business Logic:
        1. Decode the token.
        2. Check if token is blacklisted.
        3. Ensure user exists.
        
        Args:
            token (str): Reset password token

        Returns:
            bool: Whether the token is valid
        
        Raises:
            HTTPException: Invalid token
            HTTPException: Token has been revoked
            HTTPException: User not found
        """
        try:
            # Business Logic 1: Decode the token
            payload = decode_token(token)
            user_id = payload.get("sub")
        except HTTPException:
            raise
        except JWTError as e:
            logger.error(f"Failed to decode token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Business Logic 2: Check if token is blacklisted
        if self.blacklist_repository.is_blacklisted(token):
            logger.error(f"Token has been revoked")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )
        
        # Business Logic 3: Ensure user exists
        user = self.user_repository.get_user(user_id)
        if not user:
            logger.error(f"Failed to verify reset password, user not found for id: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return True

    @log_operation(logger)
    async def reset_password(self, token: str, updated_password: PasswordUpdate) -> dict:
        """
        Reset user's password using the provided token
        
        Business Logic:
        1. Verify the reset password token.
        2. Ensure user exists.
        3. Verify old password
        4. Enforce password complexity.
        5. Ensure new password and confirmation match.
        6. Update user's password in the database.
        7. Invalidate token by blacklisting them.
        
        Args:
            token (str): Reset password token
            updated_password (PasswordUpdate): New password data
            
        Returns:
            dict: Success message
            
        Raises:
            HTTPException: Password does not meet complexity requirements
        """
        # Business Logic 1: Verify the reset password token
        try:
            payload = decode_token(token)
            user_id = payload.get("sub")
            expires_at = payload.get("exp")
        except HTTPException:
            raise
        except JWTError as e:
            logger.error(f"Failed to decode token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Business Logic 2: Ensure user exists
        user = self.user_repository.get_user(user_id)
        if not user:
            logger.error(f"Failed to reset password, user not found for id: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        # Business Logic 3: Verify old password
        if not verify_password(updated_password.old_password, user.hashed_password):
            logger.error(f"Failed to reset password, incorrect old password for user id: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Old password is incorrect"
            )
        
        # Business Logic 4: Enforce password complexity
        if not UserModel.validate_password_complexity(updated_password.new_password):
            logger.error(f"Failed to reset password, password does not meet complexity requirements for user id: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password does not meet complexity requirements"
            )
            
        # Business Logic 5: Ensure new password and confirmation match
        if updated_password.new_password != updated_password.password_confirm:
            logger.error(f"Failed to reset password, new password and confirmation do not match for user id: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password and confirmation do not match"
            )
            
        # Business Logic 6: Update user's password in the database
        self.user_repository.update_user(
            user_id=user_id,
            user=UserUpdate(password=updated_password.new_password)
        )
        
        # Business Logic 7: Invalidate token by blacklisting them
        self.blacklist_repository.add_to_blacklist(token, expires_at=expires_at, token_type=TokenType.RESET_PASSWORD)
        
        return {"message": "Password reset successfully"}
