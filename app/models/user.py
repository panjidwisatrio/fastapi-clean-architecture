import secrets
import string
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.config import settings
from app.core.logging import setup_logger, log_operation

logger = setup_logger("user_model")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"))
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    last_active = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    role = relationship("Role", back_populates="users")
    otps = relationship("OTP", back_populates="user", cascade="all, delete-orphan")

    @staticmethod
    @log_operation(logger)
    def validate_email_domain(email: str) -> bool:
        """Validate if the email domain is accepted."""
        return email.split("@")[-1] in settings.accepted_email_domains

    @staticmethod
    @log_operation(logger)
    def validate_password_complexity(password: str) -> bool:
        """Validate password complexity: at least 8 characters, one digit, one uppercase letter"""
        return len(password) >= 8 and any(char.isdigit() for char in password) and any(char.isupper() for char in password)
    
    @staticmethod
    @log_operation(logger)
    def generate_random_password(length: int = 12) -> str:
        """Generate a secure random password"""
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(characters) for _ in range(length))
        return password