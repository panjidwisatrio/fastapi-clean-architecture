from fastapi import HTTPException, status
from app.core.logging import setup_logger, log_operation
from app.repositories.role_repository import RoleRepository
from app.repositories.permission_repository import PermissionRepository
from app.schemas.role import RoleCreate, Role

logger = setup_logger("role_services")

class RoleService:
    def __init__(self, role_repository: RoleRepository, permission_repository: PermissionRepository):
        self.role_repository = role_repository
        self.permission_repository = permission_repository

    @log_operation(logger)
    def create_role(self, role: RoleCreate) -> Role:
        existing_role = self.role_repository.get_role_by_name(role.role_name)
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role already exists"
            )
        return self.role_repository.create_role(role)

    @log_operation(logger)
    def get_role(self, role_id: int) -> Role:
        role = self.role_repository.get_role(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return role

    @log_operation(logger)
    def get_roles(self, skip: int = 0, limit: int = 100) -> list[Role]:
        return self.role_repository.get_roles(skip, limit)

    @log_operation(logger)
    def delete_role(self, role_id: int) -> Role:
        db_role = self.role_repository.delete_role(role_id)
        if not db_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return db_role

    @log_operation(logger)
    def add_permission_to_role(self, role_id: int, permission_id: int) -> Role:
        # Verify permission exists
        permission = self.permission_repository.get_permission(permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        
        # Add permission to role
        db_role = self.role_repository.add_permission_to_role(role_id, permission_id)
        if not db_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return db_role

    @log_operation(logger)
    def remove_permission_from_role(self, role_id: int, permission_id: int) -> Role:
        db_role = self.role_repository.remove_permission_from_role(role_id, permission_id)
        if not db_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return db_role
