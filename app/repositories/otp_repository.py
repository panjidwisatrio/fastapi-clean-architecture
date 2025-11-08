from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import Optional
from datetime import datetime, timezone

from app.core.logging import log_operation, setup_logger
from app.core.utils import get_current_utc_time
from app.models.otp import OTP, OTPType

logger = setup_logger("otp_repositories")

class OTPRepository:
    def __init__(self, db: Session):
        self.db = db
    
    @log_operation(logger)
    def create(self, email: str, code: str, type: OTPType, expires_at: datetime, user_id: Optional[int] = None) -> OTP:
        """Create new OTP"""
        otp = OTP(
            user_id=user_id,
            email=email,
            code=code,
            type=type,
            expires_at=expires_at
        )
        self.db.add(otp)
        self.db.commit()
        self.db.refresh(otp)
        return otp
    
    @log_operation(logger)
    def get_valid_otp(self, email: str, code: str, type: OTPType) -> Optional[OTP]:
        """Get valid OTP that is not used and not expired"""
        now = get_current_utc_time()
        return self.db.query(OTP).filter(
            and_(
                OTP.email == email,
                OTP.code == code,
                OTP.type == type,
                OTP.is_used == 0,
                OTP.expires_at > now
            )
        ).first()

    @log_operation(logger)
    def get_latest_otp(self, email: str, type: OTPType) -> Optional[OTP]:
        """Get latest OTP for email and type"""
        return self.db.query(OTP).filter(
            and_(
                OTP.email == email,
                OTP.type == type
            )
        ).order_by(desc(OTP.created_at)).first()
    
    @log_operation(logger)
    def mark_as_used(self, otp: OTP) -> OTP:
        """Mark OTP as used"""
        otp.is_used = 1
        self.db.commit()
        self.db.refresh(otp)
        return otp
    
    @log_operation(logger)
    def invalidate_previous_otps(self, email: str, type: OTPType):
        """Invalidate all previous OTPs for email and type"""
        self.db.query(OTP).filter(
            and_(
                OTP.email == email,
                OTP.type == type,
                OTP.is_used == 0
            )
        ).update({"is_used": 1})
        self.db.commit()
    
    @log_operation(logger)
    def delete_expired_otps(self):
        """Delete all expired OTPs"""
        now = get_current_utc_time()
        self.db.query(OTP).filter(OTP.expires_at < now).delete()
        self.db.commit()