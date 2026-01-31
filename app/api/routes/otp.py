from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_otp_service
from app.services.otp_service import OTPService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/otp", tags=["otp"])

        
@router.delete("/cleanup-expired", status_code=status.HTTP_200_OK)
async def cleanup_expired_otps(
    otp_service: OTPService = Depends(get_otp_service)
):
    """
    Cleanup expired OTPs from the database
    """
    try:
        deleted_count = otp_service.cleanup_expired_otps()
        return {"message": f"Cleaned up {deleted_count} expired OTPs"}
    except Exception as e:
        logger.error(f"Error cleaning up expired OTPs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cleanup expired OTPs"
        )