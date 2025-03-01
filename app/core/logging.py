import logging
import asyncio
import logging
from functools import wraps
from concurrent_log_handler import ConcurrentRotatingFileHandler
from fastapi import Request
from pathlib import Path

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

def setup_logger(name, level=logging.INFO, max_bytes=1024 * 1024 * 5, backup_count=10):
    # Configure logging
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    if not logger.handlers:
        # Create concurrent rotating file handler
        file_handler = ConcurrentRotatingFileHandler(
            f"logs/app.log",
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

async def log_request(logger, request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        raise
    
def log_operation(logger):
    """
    Decorator to log the start and end of operations.
    Modified to prevent duplicate logging.
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger.info(f"Starting operation: {func.__name__}")
            try:
                result = await func(*args, **kwargs)
                logger.info(f"Completed operation: {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"Operation failed: {func.__name__} - {str(e)}")
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger.info(f"Starting operation: {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"Completed operation: {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"Operation failed: {func.__name__} - {str(e)}")
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator
