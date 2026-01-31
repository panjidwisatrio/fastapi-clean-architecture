import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from app.core.database import Base


class TokenType(str, enum.Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    RESET_PASSWORD = "reset_password"


class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    type = Column(SQLEnum(TokenType), nullable=False)
    blacklisted_at = Column(DateTime(timezone=True), index=True, server_default=func.now())
    expires_at = Column(DateTime(timezone=True), index=True, nullable=False)