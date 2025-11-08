from pydantic import BaseModel, EmailStr

from app.schemas.user import UserBase


class UserRegister(UserBase):
    password: str
    password_confirm: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ForgotPasswordResponse(BaseModel):
    message: str
    email: str