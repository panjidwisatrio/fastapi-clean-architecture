from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: Optional[int] = None

class TokenPayload(BaseModel):
    sub: Optional[int] = None
    
class TokenBlacklist(BaseModel):
    token: str