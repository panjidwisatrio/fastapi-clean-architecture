from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.core.logging import setup_logger, log_operation
from app.core.utils import get_current_utc_time
from app.models.token_blacklist import TokenBlacklist
from app.core.config import settings

logger = setup_logger("token_blacklist_repositories")

class TokenBlacklistRepository:
    def __init__(self, db: Session):
        self.db = db
    
    @log_operation(logger)
    def add_to_blacklist(self, token: str, expires_at: datetime) -> TokenBlacklist:
        """Add a token to the blacklist"""
        db_blacklist = TokenBlacklist(
            token=token,
            expires_at=expires_at
        )
        self.db.add(db_blacklist)
        self.db.commit()
        self.db.refresh(db_blacklist)
        return db_blacklist
    
    @log_operation(logger)
    def is_blacklisted(self, token: str) -> bool:
        """Check if a token is blacklisted"""
        return self.db.query(TokenBlacklist).filter(
            TokenBlacklist.token == token
        ).first() is not None
    
    @log_operation(logger)
    def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens from blacklist"""
        count = self.db.query(TokenBlacklist).filter(
            TokenBlacklist.expires_at < get_current_utc_time()
        ).delete()
        self.db.commit()
        return count
    
    @log_operation(logger)
    def get_all_blacklisted_tokens(self, skip: int = 0, limit: int = 100) -> list[TokenBlacklist]:
        """Get all blacklisted tokens (for admin purposes)"""
        return self.db.query(TokenBlacklist).offset(skip).limit(limit).all()