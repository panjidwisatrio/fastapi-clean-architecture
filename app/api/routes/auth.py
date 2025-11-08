
import logging

from fastapi import APIRouter, Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import get_auth_service, get_otp_service
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import User as UserSchema
from app.schemas.auth import ForgotPasswordRequest, ForgotPasswordResponse, UserRegister
from app.schemas.token import Token
from app.services.auth_service import AuthService
from app.services.otp_service import OTPService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegister, service: AuthService = Depends(get_auth_service)):
    return await service.register_user(user)

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service)
):
    user = service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = service.create_access_token(user)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    authorization: str = Header(default=None),
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Logout user by blacklisting the current access token.
    Token will be invalidated and cannot be used again.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    
    # Extract token from header
    token = authorization.split(" ")[1]
    
    # Update user's last active timestamp
    auth_service.logout_user(current_user, token=token)
    
    return {"message": "Successfully logged out"}

@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    status_code=status.HTTP_200_OK,
    summary="Request password reset",
    description="Send password reset email with OTP link"
)
async def forgot_password(
    request: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Request password reset email
    
    - **email**: User's email address
    """
    try:
        response = await auth_service.forgot_password(email=request.email)
        return ForgotPasswordResponse(
            message=response["message"],
            email=request.email
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in forgot password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process forgot password request"
        )

@router.get("/verify-forgot-password-otp", status_code=status.HTTP_200_OK)
async def verify_forgot_password_otp(
    otp: str = Header(default=None),
    otp_service: OTPService = Depends(get_otp_service),
):
    """
    Verify if the provided OTP is valid and not blacklisted.
    """
    try:
        is_valid, message = otp_service.verify_otp(otp)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=message
            )
        
        return {"is_valid": is_valid, "message": message}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying OTP: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify OTP"
        )
