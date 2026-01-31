from sqlalchemy.orm import Session
from app.core.logging import setup_logger, log_operation
from app.repositories.token_blacklist_repository import TokenBlacklistRepository

logger = setup_logger("token_blacklist_services")

class TokenBlacklistService:
    def __init__(self, db: Session):
        self.token_blacklist_repository = TokenBlacklistRepository(db)
    
    @log_operation(logger)
    def cleanup_expired_tokens(self) -> int:
        """
        Business logic for cleanup:
        1. Remove expired tokens from blacklist
        2. Log cleanup results
        """
        count = self.token_blacklist_repository.cleanup_expired_tokens()
        logger.info(f"Cleaned up {count} expired tokens from blacklist")
        return count