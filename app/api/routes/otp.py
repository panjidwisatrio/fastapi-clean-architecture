from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_otp_service
from app.schemas.otp import OTPRequest, OTPVerify, OTPResponse, OTPVerifyResponse
from app.services.otp_service import OTPService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/otp", tags=["otp"])


@router.post("/request", response_model=OTPResponse, status_code=status.HTTP_200_OK)
async def request_otp(
    request: OTPRequest,
    otp_service: OTPService = Depends(get_otp_service)
):
    """
    Request OTP code to be sent via email
    
    - **email**: User's email address
    - **type**: OTP type (register or reset_password)
    """
    try:        
        # Create OTP
        otp = await otp_service.create_otp_and_send(
            email=request.email,
            type=request.type
        )
        
        return OTPResponse(
            message=f"OTP code has been sent to {request.email}",
            expires_at=otp.expires_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error requesting OTP: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to request OTP code"
        )


@router.post("/verify", response_model=OTPVerifyResponse, status_code=status.HTTP_200_OK)
async def verify_otp(
    request: OTPVerify,
    otp_service: OTPService = Depends(get_otp_service)
):
    """
    Verify OTP code
    
    - **email**: User's email address
    - **code**: 6-digit OTP code
    - **type**: OTP type (register or reset_password)
    """
    try:
        is_valid, message = otp_service.verify_otp(
            email=request.email,
            code=request.code,
            type=request.type
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        return OTPVerifyResponse(
            message=message,
            is_valid=is_valid
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying OTP: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify OTP code"
        )