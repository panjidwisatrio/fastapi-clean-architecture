from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.logging import setup_logger, log_operation
from app.repositories.role_repository import RoleRepository
from app.repositories.permission_repository import PermissionRepository
from app.repositories.user_repository import UserRepository
from app.schemas.role import PermissionRole, RoleCreate, Role, RoleUpdate
from app.services.cache_service import CacheService

logger = setup_logger("role_services")

class RoleService:
    def __init__(
        self,
        db: Session,
        cache_service: CacheService,
    ):
        self.role_repository = RoleRepository(db)
        self.permission_repository = PermissionRepository(db)
        self.user_repository = UserRepository(db)
        self.cache_service = cache_service

    @log_operation(logger)
    async def create_role(self, role: RoleCreate) -> Role:
        existing_role = self.role_repository.get_role_by_name(role.role_name)
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role already exists"
            )
        
        # Invalidate role cache
        await self.cache_service.invalidate_role_cache()
        return self.role_repository.create_role(role)
    
    @log_operation(logger)
    async def update_role(self, role_id: int, role: RoleUpdate) -> Role:
        db_role = self.role_repository.get_role(role_id)
        if not db_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        # Invalidate role cache
        await self.cache_service.invalidate_role_cache()
        return self.role_repository.update_role(role_id, role)

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
    async def delete_role(self, role_id: int) -> Role:
        """
        Delete a role by its ID
        
        Business Logic:
        - Check if the role exists; if not, raise a 404 error.
        - Check if role is superadmin; if so, prevent deletion.
        - update affected users to a default role before deletion.
        - Delete the role from the database.
        - Invalidate role cache.
        
        Args:
            role_id (int): The ID of the role to delete
            
        Returns:
            Role: The deleted role object
        """
        # Business Logic 1: Check if the role exists; if not, raise a 404 error.
        db_role = self.role_repository.get_role(role_id)
        if not db_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        # Business Logic 2: Prevent deletion of superadmin role
        if db_role.role_name.lower() == "superadmin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete superadmin role"
            )
            
        # Business Logic 3: Update affected users to a default role before deletion.
        default_role = self.role_repository.get_role_by_name("user")
        if not default_role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Default role 'user' not found. Cannot reassign users."
            )
        
        # Reassign users with the role to be deleted to the default role
        self.user_repository.update_users_role(role_id, default_role.id)
        
        # Business Logic 4: Delete the role from the database.
        db_role = self.role_repository.delete_role(role_id)
        if not db_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        # Invalidate role cache
        await self.cache_service.invalidate_role_cache()
        return db_role

    @log_operation(logger)
    def add_permission_to_role(self, permissions: PermissionRole) -> Role:
        """
        Add permission(s) to a role

        Args:
            permissions (PermissionRole): Role ID and list of Permission IDs to add

        Raises:
            HTTPException: Permission not found
            HTTPException: Role not found
            HTTPException: One or more permissions are already assigned to the role
            HTTPException: Role not found

        Returns:
            Role: The updated role object with new permissions added
        """
        # Business Logic 1: Verify permission exists
        permission = self.permission_repository.validate_permissions_exist(permissions.permission_ids)
        if not permission:
            logger.error(f"Permission IDs {permissions.permission_ids} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
            
        # Business Logic 2: Verify role exists
        role = self.role_repository.get_role(permissions.role_id)
        if not role:
            logger.error(f"Role ID {permissions.role_id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
            
        # Business Logic 3: Verify permissions are not already assigned to the role
        existing_permissions = self.role_repository.validate_permissions_exist(permissions.role_id, permissions.permission_ids)
        if len(existing_permissions) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more permissions are already assigned to the role"
            )
        
        # Business Logic 4: Add permission to role
        db_role = self.role_repository.add_permission_to_role(permissions.role_id, permissions.permission_ids)
        if not db_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        return db_role

    @log_operation(logger)
    def remove_permission_from_role(self, permissions: PermissionRole) -> Role:
        """
        Remove permission(s) from a role

        Business Logic:
        1. Verify role exists; if not, raise 404 error.
        2. Verify permissions are assigned to the role; if not, raise 400 error.
        3. Remove the permissions from the role.
        
        Args:
            permissions (PermissionRole): Role ID and list of Permission IDs to remove

        Raises:
            HTTPException: Role not found
            HTTPException: One or more permissions are not assigned to the role
        
        Returns:
            Role: The updated role object with permissions removed
        """
        # Business Logic 1: Verify role exists
        role = self.role_repository.get_role(permissions.role_id)
        if not role:
            logger.error(f"Role ID {permissions.role_id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        # Business Logic 2: Verify permissions are assigned to the role
        existing_permissions = self.role_repository.validate_permissions_exist(permissions.role_id, permissions.permission_ids)
        if len(existing_permissions) != len(permissions.permission_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more permissions are not assigned to the role"
            )
        
        # Business Logic 3: Remove permission from role
        db_role = self.role_repository.remove_permission_from_role(permissions.role_id, permissions.permission_ids)
        if not db_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        return db_role