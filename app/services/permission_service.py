from fastapi import HTTPException, status
from app.core.logging import setup_logger, log_operation
from app.repositories.permission_repository import PermissionRepository
from app.schemas.permission import PermissionCreate, Permission

logger = setup_logger("permission_services")

class PermissionService:
    def __init__(self, permission_repository: PermissionRepository):
        self.permission_repository = permission_repository

    @log_operation(logger)
    def create_permission(self, permission: PermissionCreate) -> Permission:
        existing_permission = self.permission_repository.get_permission_by_name(permission.permission_name)
        if existing_permission:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission already exists"
            )
        return self.permission_repository.create_permission(permission)

    @log_operation(logger)
    def get_permission(self, permission_id: int) -> Permission:
        permission = self.permission_repository.get_permission(permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        return permission

    @log_operation(logger)
    def get_permissions(self, skip: int = 0, limit: int = 100) -> list[Permission]:
        return self.permission_repository.get_permissions(skip, limit)

    @log_operation(logger)
    def delete_permission(self, permission_id: int) -> Permission:
        db_permission = self.permission_repository.delete_permission(permission_id)
        if not db_permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        return db_permission
