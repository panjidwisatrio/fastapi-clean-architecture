from typing import Optional, List
from app.core.cache import CacheKeyBuilder

class CacheService:
    """Service for managing cache invalidation"""
    
    @staticmethod
    async def invalidate_user_cache():
        """Invalidate user-related cache"""
        await CacheKeyBuilder.increment_version("users")
    
    @staticmethod
    async def invalidate_role_cache():
        """Invalidate role-related cache"""
        await CacheKeyBuilder.increment_version("roles")
    
    @staticmethod
    async def invalidate_permission_cache():
        """Invalidate permission-related cache"""
        await CacheKeyBuilder.increment_version("permissions")
    
    @staticmethod
    async def invalidate_otp_cache():
        """Invalidate OTP-related cache"""
        await CacheKeyBuilder.increment_version("otp")
    
    @staticmethod
    async def invalidate_multiple(namespaces: List[str]):
        """Invalidate multiple namespaces"""
        for namespace in namespaces:
            await CacheKeyBuilder.increment_version(namespace)