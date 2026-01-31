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
    def __init__(self, db: Session):
        self.db = db
        self.otp_repo = OTPRepository(db)
    
    @log_operation(logger)
    def cleanup_expired_otps(self):
        """Clean up expired OTPs"""
        self.otp_repo.delete_expired_otps()