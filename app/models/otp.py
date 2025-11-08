import secrets
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta, timezone
import enum

from app.core.config import settings
from app.core.database import Base
from app.core.logging import setup_logger, log_operation
from app.core.utils import get_current_utc_time


logger = setup_logger("otp_model")

class OTPType(str, enum.Enum):
    REGISTER = "register"
    RESET_PASSWORD = "reset_password"


class OTP(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    email = Column(String(255), nullable=False, index=True)
    code = Column(String(6), nullable=False)
    type = Column(SQLEnum(OTPType), nullable=False)
    is_used = Column(Integer, default=0)  # 0: not used, 1: used
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=get_current_utc_time())
    
    # Relationship
    user = relationship("User", back_populates="otps")
    
    @staticmethod
    @log_operation(logger)
    def generate_code() -> str:
        """Generate OTP code"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(settings.OTP_LENGTH)])

    @staticmethod
    @log_operation(logger)
    def get_expiry_time() -> datetime:
        """Get OTP expiry time (configured minutes from now)"""
        return get_current_utc_time() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)