import os
from app.core.config import get_settings

def test_environment_settings():
    # Get current environment variable
    current_env = os.environ.get("ENVIRONMENT", "Not set (will default to development)")
    print(f"Current ENVIRONMENT variable: {current_env}")
    
    # Load settings based on current environment
    settings = get_settings()
    
    # Print loaded settings
    print("\nLoaded settings:")
    print(f"- ENVIRONMENT: {settings.ENVIRONMENT}")
    print(f"- ACCESS_TOKEN_EXPIRE_MINUTES: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")
    print(f"- DATABASE_URL: {settings.DATABASE_URL}")
    print(f"- is_development: {settings.is_development}")
    print(f"- is_testing: {settings.is_testing}")
    print(f"- is_production: {settings.is_production}")
    
    # Identify which env file was used
    env_file = f".env.{settings.ENVIRONMENT}" if os.path.exists(f".env.{settings.ENVIRONMENT}") else ".env"
    print(f"\nSettings loaded from: {env_file}")

if __name__ == "__main__":
    test_environment_settings()
