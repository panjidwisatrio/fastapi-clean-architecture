from passlib.context import CryptContext
import json
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def load_permissions():
    """Load permissions from the JSON file."""
    permissions_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "permissions.json")
    with open(permissions_path, 'r') as f:
        permissions_data = json.load(f)
    
    return permissions_data
