from typing import Callable, Optional, Any
from fastapi import Request, Response
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
import hashlib
import json
from app.core.config import redis
from app.core.logging import setup_logger

logger = setup_logger("cache")

class CacheKeyBuilder:
    """Versioned cache key builder for cache invalidation"""
    
    @staticmethod
    async def get_version(namespace: str) -> str:
        """Get current version for a namespace"""
        client = redis.get_client()
        version = await client.get(f"cache_version:{namespace}")
        logger.info(f"Fetched cache version for namespace '{namespace}': {version}")
        
        if version:
            # Handle both bytes and str types from different Redis clients
            if isinstance(version, bytes):
                decoded_version = version.decode('utf-8')
            else:
                decoded_version = str(version)
            
            logger.info(f"Cache version for namespace '{namespace}': {decoded_version}")
            return decoded_version  
        
        # Initialize version to 1 if not exists
        await client.set(f"cache_version:{namespace}", "1")
        logger.info(f"Initialized cache version for namespace '{namespace}' to 1")
        return "1"
    
    @staticmethod
    async def increment_version(namespace: str) -> None:
        """Increment version to invalidate cache"""
        client = redis.get_client()
        
        new_version = await client.incr(f"cache_version:{namespace}")
        logger.info(f"Incremented cache version for namespace '{namespace}' to {new_version}")
    
    @staticmethod
    async def build_key(
        func: Callable,
        namespace: str,
        request: Request = None,
        response: Response = None,
        args: tuple = None,
        kwargs: dict = None,
    ) -> str:
        """Build versioned cache key"""
        logger.info(f"Building cache key for function '{func.__name__}' in namespace '{namespace}'")
        
        version = await CacheKeyBuilder.get_version(namespace)
        
        # Build base key from function and parameters
        prefix = f"{namespace}:v{version}"
        
        # Include request parameters
        cache_key_parts = [prefix, func.__module__, func.__name__]
        logger.info(f"Building cache key parts: {cache_key_parts} with version {version}")
        
        if request:
            # Include query parameters
            if request.query_params:
                query_hash = hashlib.md5(
                    json.dumps(dict(request.query_params), sort_keys=True).encode()
                ).hexdigest()
                cache_key_parts.append(f"query:{query_hash}")
            
            # Include path parameters
            if request.path_params:
                path_hash = hashlib.md5(
                    json.dumps(request.path_params, sort_keys=True).encode()
                ).hexdigest()
                cache_key_parts.append(f"path:{path_hash}")
        
        final_key = ":".join(cache_key_parts)
        logger.info(f"Built cache key: {final_key}")
        return final_key

def create_key_builder(namespace: str):
    """Factory function to create key builder for specific namespace"""
    async def key_builder(
        func: Callable,
        *args,
        **kwargs
    ) -> str:
        """
        Key builder that accepts variable arguments from fastapi-cache2
        Expected call: key_builder(func, namespace, request, response, *args, **kwargs)
        But we ignore the namespace from fastapi-cache and use our captured one
        """
        logger.info(f"key_builder called with captured namespace: '{namespace}'")
        logger.info(f"Received args: {len(args)} positional args")
        
        request = None
        response = None
        
        if len(args) >= 2:
            # args[0] is the namespace string from fastapi-cache (we ignore it)
            request = args[1] if len(args) > 1 else None
            response = args[2] if len(args) > 2 else None
        
        # Also check kwargs
        request = kwargs.get('request', request)
        response = kwargs.get('response', response)
        
        # Use namespace from closure (captured from create_key_builder call)
        return await CacheKeyBuilder.build_key(
            func=func,
            namespace=namespace,
            request=request,
            response=response,
            args=args[3:] if len(args) > 3 else None,  # Remaining args after func, ns, req, res
            kwargs=kwargs
        )
    
    return key_builder

# Cache decorators for different namespaces
def cache_user(expire: int = 300):
    """Cache decorator for user endpoints"""
    return cache(
        expire=expire,
        key_builder=create_key_builder("users")
    )

def cache_role(expire: int = 600):
    """Cache decorator for role endpoints"""
    return cache(
        expire=expire,
        key_builder=create_key_builder("roles")
    )

def cache_permission(expire: int = 600):
    """Cache decorator for permission endpoints"""
    return cache(
        expire=expire,
        key_builder=create_key_builder("permissions")
    )

def cache_otp(expire: int = 60):
    """Cache decorator for OTP endpoints"""
    return cache(
        expire=expire,
        key_builder=create_key_builder("otp")
    )

async def invalidate_cache(namespace: str):
    """Invalidate all cache for a namespace"""
    await CacheKeyBuilder.increment_version(namespace)