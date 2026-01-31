
import logging

from fastapi import APIRouter, Depends, HTTPException, Header, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import get_auth_service
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import PasswordUpdate, User as UserSchema
from app.schemas.auth import AuthResponseBase, ForgotPasswordRequest, ForgotPasswordResponse, ResendVerificationOTPRequest, UserRegister, VerifyEmailRequest
from app.schemas.token import Token
from app.services.auth_service import AuthService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegister, service: AuthService = Depends(get_auth_service)):
    return await service.register_user(user)

@router.post("/login", response_model=Token)
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service)
):
    access_token, refresh_token, expires_in, max_age = service.authenticate_user(form_data.username, form_data.password)
    response.set_cookie(
        key="refresh_token", 
        value=refresh_token, 
        httponly=True, # Mitigates XSS attacks
        secure=True, # Ensures cookie is sent over HTTPS only
        samesite=None, # Adjust based on your cross-site requirements; 'Lax' or 'Strict' can be used; None allows cross-site;
        max_age=max_age,
        path="/auth/refresh-token"
    )
    return {"access_token": access_token, "token_type": "bearer", "expires_in": expires_in}

@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    request: Request,
    service: AuthService = Depends(get_auth_service)
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token, expires_in = service.refresh_access_token(refresh_token)
    return {"access_token": access_token, "token_type": "bearer", "expires_in": expires_in}

@router.post("/logout", status_code=status.HTTP_200_OK, response_model=AuthResponseBase)
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
    forgot_password_request: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Request password reset email
    
    - **email**: User's email address
    """
    try:
        response = await auth_service.forgot_password(forgot_password_request=forgot_password_request)
        return ForgotPasswordResponse(
            message=response["message"],
            expires_in=response["expires_in"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in forgot password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process forgot password request"
        )

@router.get("/verify-reset-password", status_code=status.HTTP_200_OK, response_model=AuthResponseBase)
async def verify_reset_password(
    token: str = Header(default=None),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Verify if the provided OTP is valid and not blacklisted.
    """
    try:
        _ = await auth_service.verify_reset_password(token=token)
        return {"message": "OTP is valid"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying forgot password OTP: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify OTP"
        )
        
@router.post("/verify-email", status_code=status.HTTP_200_OK, response_model=AuthResponseBase)
async def verify_email(
    verify_request: VerifyEmailRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Verify user's email using OTP code
    
    - **email**: User's email address
    - **otp_code**: OTP code sent to user's email
    """
    try:
        _ = await auth_service.verify_email(verify_request)
        return {"message": "Email verified successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify email"
        )

@router.post("/resend-verification-otp", status_code=status.HTTP_200_OK, response_model=AuthResponseBase)
async def resend_verification_otp(
    resend_request: ResendVerificationOTPRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Resend verification OTP to user's email
    
    - **email**: User's email address
    """
    try:
        _ = await auth_service.resend_verification_otp(resend_request=resend_request)
        return {"message": "Verification OTP resent successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resending verification OTP: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resend verification OTP"
        )
        
@router.post("/reset-password", status_code=status.HTTP_200_OK, response_model=AuthResponseBase)
async def reset_password(
    request: PasswordUpdate,
    token: str = Header(default=None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Reset user's password using OTP token
    
    - **token**: OTP token sent to user's email
    - **new_password**: New password to set
    """
    try:
        _ = await auth_service.reset_password(token=token, updated_password=request)
        return {"message": "Password reset successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )