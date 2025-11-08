import random
import string
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional


from app.core.logging import log_operation
from app.core.utils import get_current_utc_time
from app.models.otp import OTP, OTPType
from app.repositories.otp_repository import OTPRepository
import logging

from app.schemas.user import UserUpdate
from app.services.email_service import EmailService
from app.services.user_service import UserService

logger = logging.getLogger("otp_services")


class OTPService:
    def __init__(self, db: Session, user_service: UserService, email_service: EmailService):
        self.db = db
        self.otp_repo = OTPRepository(db)
        self.user_service = user_service
        self.email_service = email_service

    @log_operation(logger)
    async def create_otp_and_send(
        self,
        email: str,
        type: OTPType,
        user_id: Optional[int] = None
    ) -> OTP:
        """Create OTP and send via email"""
        # Business logic 1: Validate email and OTP type
        try:
            if type == OTPType.REGISTER:
                # Check if email already verified
                user = self.user_service.get_user_by_email(email)
                if user.is_verified:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already verified"
                    )
                user_id = user.id
            elif type == OTPType.RESET_PASSWORD:
                # Check if email exists
                user = self.user_service.get_user_by_email(email)
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Email not found"
                    )
                user_id = user.id
        except HTTPException as http_exc:
            if http_exc.status_code != status.HTTP_404_NOT_FOUND:
                logger.error(f"HTTP error in create_otp_and_send for email {email}: {http_exc.detail}")
                raise

        # Business logic 2: Invalidate previous OTPs
        self.otp_repo.invalidate_previous_otps(email, type)
        
        # Business logic 3: Generate OTP
        try:
            code = OTP.generate_code()
            expires_at = OTP.get_expiry_time()
        except Exception as e:
            logger.error(f"Error generating OTP code: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate OTP code"
            )

        # Business logic 4: Save to database
        otp = self.otp_repo.create(
            email=email,
            code=code,
            type=type,
            expires_at=expires_at,
            user_id=user_id
        )
        
        # Business logic 4: Send OTP via email
        if type == OTPType.REGISTER:
            email_sent = await self.email_service.send_otp_email(
                to_email=email,
                otp_code=code,
                otp_type=type
            )
        elif type == OTPType.RESET_PASSWORD:
            email_sent = await self.email_service.send_reset_password_email(
                to_email=email,
                otp_code=code
            )

        if not email_sent:
            logger.error(f"Failed to send OTP email to {email}")
            # You might want to raise an exception here
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send OTP email"
            )
        
        return otp
    
    @log_operation(logger)
    def verify_otp(self, email: str, code: str, type: OTPType) -> tuple[bool, Optional[str]]:
        """Verify OTP code"""
        # Business logic 1: Check if OTP is valid
        otp = self.otp_repo.get_valid_otp(email, code, type)
        
        if not otp:
            # Check if OTP exists but expired or used
            latest_otp = self.otp_repo.get_latest_otp(email, type)
            if latest_otp:
                if latest_otp.is_used == 1:
                    return False, "OTP code already used"
                elif latest_otp.expires_at < get_current_utc_time():
                    return False, "OTP code expired"
            return False, "Invalid OTP code"
        
        # Business logic 2: Perform post-verification actions
        if type == OTPType.REGISTER:
            # Mark user as verified
            self.user_service.update_user(email=email, user=UserUpdate(is_verified=True))
        elif type == OTPType.RESET_PASSWORD:
            # TODO: Additional logic for password reset can be added here
            pass
        
        # Business logic 3: Mark OTP as used
        self.otp_repo.mark_as_used(otp)
        
        return True, "OTP code verified successfully"
    
    @log_operation(logger)
    def cleanup_expired_otps(self):
        """Clean up expired OTPs"""
        self.otp_repo.delete_expired_otps()