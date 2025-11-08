from datetime import datetime, timezone
from jose import jwt, JWTError
from fastapi import HTTPException, status
from app.core.logging import setup_logger, log_operation
from app.repositories.token_blacklist_repository import TokenBlacklistRepository
from app.core.config import settings

logger = setup_logger("token_blacklist_services")

class TokenBlacklistService:
    def __init__(self, token_blacklist_repository: TokenBlacklistRepository):
        self.token_blacklist_repository = token_blacklist_repository
    
    @log_operation(logger)
    def blacklist_token(self, token: str) -> None:
        """
        Business logic for blacklisting a token:
        1. Decode token to get expiration time
        2. Add token to blacklist with expiration
        3. Log the blacklist action
        """
        try:
            # Decode token to get expiration time
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            exp = payload.get("exp")
            
            if exp is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid token: no expiration"
                )
            
            # Convert exp timestamp to datetime
            expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
            
            # Check if token is already blacklisted
            if self.token_blacklist_repository.is_blacklisted(token):
                logger.warning(f"Token already blacklisted")
                return
            
            # Add to blacklist
            self.token_blacklist_repository.add_to_blacklist(token, expires_at)
            logger.info(f"Token successfully blacklisted, expires at {expires_at}")
            
        except JWTError as e:
            logger.error(f"Failed to decode token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )
    
    @log_operation(logger)
    def is_token_blacklisted(self, token: str) -> bool:
        """Check if a token is blacklisted"""
        return self.token_blacklist_repository.is_blacklisted(token)
    
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