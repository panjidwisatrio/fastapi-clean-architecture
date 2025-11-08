import os
import re
from pydantic import BaseSettings
from functools import lru_cache

def resolve_env_vars(value: str) -> str:
    """
    Resolve environment variables in string values.
    Replaces ${VARIABLE_NAME} with the value of the environment variable.
    """
    if not isinstance(value, str):
        return value
        
    pattern = r'\${([^}]*)}'
    matches = re.findall(pattern, value)
    
    for match in matches:
        env_var = os.environ.get(match)
        if (env_var is not None):
            value = value.replace(f'${{{match}}}', env_var)
    
    return value

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ACCEPTED_EMAIL_DOMAINS: str = "global.ntt,ntt.com,nttdata.com"
    DATABASE_URL: str
    
    # Frontend Configuration (Frontend URL, Endpoints, etc.)
    APP_URL: str = "http://localhost:5000"
    RESET_PASSWORD_ENDPOINT: str = "/users/reset-password"
    
    # Gmail SMTP Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: str
    SMTP_FROM_NAME: str = "Your App"
    
    # OTP Configuration
    OTP_EXPIRE_MINUTES: int = 5
    OTP_LENGTH: int = 6

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
        env_file_env_var = "SETTINGS_ENV_FILE"
        
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT.lower() == "testing"
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def accepted_email_domains(self) -> list[str]:
        return [domain.strip() for domain in self.ACCEPTED_EMAIL_DOMAINS.split(",")]


@lru_cache()
def get_settings():
    environment = os.environ.get("ENVIRONMENT", "development")
    env_file = f".env.{environment}"
    
    # Fallback to .env if specific environment file doesn't exist
    if not os.path.exists(env_file):
        env_file = ".env"
    
    settings = Settings(_env_file=env_file)
    
    # Apply environment variable substitution for production
    if settings.is_production:
        if isinstance(settings.SECRET_KEY, str) and '${' in settings.SECRET_KEY:
            settings.SECRET_KEY = resolve_env_vars(settings.SECRET_KEY)
        
        if isinstance(settings.DATABASE_URL, str) and '${' in settings.DATABASE_URL:
            settings.DATABASE_URL = resolve_env_vars(settings.DATABASE_URL)
    
    return settings

settings = get_settings()
