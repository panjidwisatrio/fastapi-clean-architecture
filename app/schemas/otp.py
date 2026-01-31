from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from app.models.otp import OTPType
    
    
class OTPInDB(BaseModel):
    id: int
    user_id: Optional[int]
    email: str
    code: str
    type: OTPType
    is_used: int
    expires_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True