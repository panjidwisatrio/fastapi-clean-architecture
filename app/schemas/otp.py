from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from app.models.otp import OTPType


class OTPRequest(BaseModel):
    email: EmailStr
    type: OTPType


class OTPVerify(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)
    type: OTPType


class OTPResponse(BaseModel):
    message: str
    expires_at: datetime


class OTPVerifyResponse(BaseModel):
    message: str
    is_valid: bool
    
    
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