from pydantic import BaseModel, EmailStr

from app.schemas.user import UserBase

class AuthResponseBase(BaseModel):
    message: str

class UserRegister(UserBase):
    password: str
    password_confirm: str

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp_code: str

class ResendVerificationOTPRequest(BaseModel):
    email: EmailStr

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ForgotPasswordResponse(AuthResponseBase):
    expires_in: int