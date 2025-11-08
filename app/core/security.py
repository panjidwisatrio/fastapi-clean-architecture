from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.core.utils import load_permissions
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.core.config import settings

# Security configuration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Load permissions from JSON file using the utility function
permissions_data = load_permissions()
SCOPES = permissions_data.get("scopes", {})

# Update OAuth2 scheme to support scopes loaded from JSON
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login",
    scopes=SCOPES
)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.now(datetime.timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    # Ensure subject is a string
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        
        # Convert string user ID to integer
        user_id = int(user_id_str)
        
        # Fetch user from database
        user_repo = UserRepository(db)
        user = user_repo.get_user(user_id)
        if user is None:
            raise credentials_exception
            
        # Check required scopes
        if security_scopes.scopes:
            # Get user permissions
            user_permissions = []
            if user.role:
                user_permissions = [p.permission_name for p in user.role.permissions]
                
            # Check if user has any of the required permissions
            for scope in security_scopes.scopes:
                if scope in user_permissions:
                    # User has at least one required permission
                    break
            else:
                # User doesn't have any of the required permissions
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": authenticate_value},
                )
                
        return user
    except (JWTError, ValueError):
        raise credentials_exception
