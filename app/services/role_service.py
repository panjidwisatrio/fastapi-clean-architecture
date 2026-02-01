from typing import Union
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.logging import setup_logger, log_operation
from app.repositories.role_repository import RoleRepository
from app.repositories.permission_repository import PermissionRepository
from app.repositories.user_repository import UserRepository
from app.schemas.role import FailedAssignment, PermissionRole, RoleCreate, Role, RoleUpdate, UserAssignmentResult, UserUnassignmentResult, UsersRoleAssignment

logger = setup_logger("role_services")

class RoleService:
    def __init__(
        self,
        db: Session
    ):
        self.role_repository = RoleRepository(db)
        self.permission_repository = PermissionRepository(db)
        self.user_repository = UserRepository(db)

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
    def update_role(self, role_id: int, role: RoleUpdate) -> Role:
        db_role = self.role_repository.get_role(role_id)
        if not db_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return self.role_repository.update_role(role_id, role)

    @log_operation(logger)
    def set_default_role(self, role_id: int) -> Role:
        """
        Set a role as the default role
        
        Business Logic:
        1. Verify role exists; if not, raise 404 error.
        2. Prevent super admin or admin role to be default
        3. Check if current role is already default; if so, return it.
        4. Set role as default and unset previous default role.
        
        Args:
            role_id (int): The ID of the role to set as default
        
        Raises:
            HTTPException: Role not found
            HTTPException: Failed to set default role
        
        Returns:
            Role: The updated role object set as default
        """
        # Business Logic 1: Verify role exists
        db_role = self.role_repository.get_role(role_id)
        if not db_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
            
        # Business Logic 2: Prevent super admin or admin role to be default (contain admin in name)
        if "admin" in db_role.role_name.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot set superadmin or admin role as default"
            )
        
        # Business Logic 3: Check if current role is already default; if so, return it.
        if db_role.is_default:
            return db_role
        
        # Business Logic 4: Set role as default and unset previous default role.
        default_role = self.role_repository.set_role_as_default(role_id)
        if not default_role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to set default role"
            )
            
        return default_role
    
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
    def get_default_role(self) -> Role:
        role = self.role_repository.get_default_role()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Default role not found"
            )
        return role
    
    @log_operation(logger)
    def get_roles(self, skip: int = 0, limit: int = 100) -> list[Role]:
        return self.role_repository.get_roles(skip, limit)

    @log_operation(logger)
    def delete_role(self, role_id: int) -> Role:
        """
        Delete a role by its ID
        
        Business Logic:
        - Check if the role exists; if not, raise a 404 error.
        - Check if role is superadmin; if so, prevent deletion.
        - update affected users to a default role before deletion.
        - Delete the role from the database.
        
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
    
    @log_operation(logger)
    def assign_role_to_users(self, assignment: UsersRoleAssignment) -> Union[Role, UserAssignmentResult]:
        """
        Assign users to a role

        Business Logic:
        1. Verify role exists; if not, raise 404 error.
        2. Verify users are available; if not, add error 404 for respective user to list.
        3. Verify users are verified; if not, add error 403 for respective user to list.
        4. Verify users are active; if not, add error 403 for respective user to list.
        5. Verify users are not already assigned to the role; if so, add error 409 for respective user to list.
        6. filter out invalid users and assign valid users to the role.
        7. If any errors were collected and some are valid assignments, return 207 Multi-Status with details.
        8. If all users failed validation, raise HTTPException with 400 Bad Request and details.
        9. If all users were successfully assigned, return the updated role.
        
        Args:
            assignment (UsersRoleAssignment): Role ID and list of User IDs to assign

        Raises:
            HTTPException: Role not found
        
        Returns:
            Role: The updated role object with users assigned
        """
        # Business Logic 1: Verify role exists
        role = self.role_repository.get_role(assignment.role_id)
        if not role:
            logger.error(f"Role ID {assignment.role_id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        # Business Logic 2: Validate users
        errors = []
        valid_user_ids = []
        for user_id in assignment.user_ids:
            user = self.user_repository.get_user(user_id)
            if not user:
                errors.append(FailedAssignment(user_id=user_id, reason="User not found").dict())
                continue
            if not user.is_verified:
                errors.append(FailedAssignment(user_id=user_id, reason="User not verified").dict())
                continue
            if not user.is_active:
                errors.append(FailedAssignment(user_id=user_id, reason="User not active").dict())
                continue
            if user.role_id == assignment.role_id:
                errors.append(FailedAssignment(user_id=user_id, reason="User already assigned to this role").dict())
                continue
            valid_user_ids.append(user_id)
        
        # Business Logic 3: Assign valid users to the role
        if valid_user_ids:
            if not self.role_repository.add_users_to_role(assignment.role_id, valid_user_ids):
                logger.error(f"Failed to assign users {valid_user_ids} to role ID {assignment.role_id}.")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to assign users to role"
                )
        
        # Business Logic 4: Handle response based on errors and valid assignments
        if errors and valid_user_ids:
            return UserAssignmentResult(
                failed_assignments=errors,
                **self.role_repository.get_role(assignment.role_id).dict()
            )
        elif errors and not valid_user_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=errors
            )
        
        return self.role_repository.get_role(assignment.role_id)
    
    @log_operation(logger)
    def unassign_role_from_users(self, assignment: UsersRoleAssignment) -> Union[Role, UserUnassignmentResult]:
        """
        Unassign users from a role

        Business Logic:
        1. Verify role exists; if not, raise 404 error.
        2. Verify if role is default role; if so, raise 403 error.
        3. Verify if default role exists; if not, raise 500 error.
        4. Verify users are available; if not, add error 404 for respective user to list.
        5. Verify users are verified; if not, add error 403 for respective user to list.
        6. Verify users are active; if not, add error 403 for respective user to list.
        7. Verify users were have another role assigned; if so, add error 409 for respective user to list.
        8. filter out invalid users and unassign valid users from the role.
        9. If any errors were collected and some are valid unassignments, return 207 Multi-Status with details.
        10. If all users failed validation, raise HTTPException with 400 Bad Request and details.
        11. If all users were successfully unassigned, return the updated role.
        
        Args:
            assignment (UsersRoleAssignment): Role ID and list of User IDs to unassign

        Raises:
            HTTPException: Role not found
            HTTPException: Role is default role
            HTTPException: Default role not found
        
        Returns:
            Role: The updated role object with users unassigned
        """
        # Business Logic 1: Verify role exists
        role = self.role_repository.get_role(assignment.role_id)
        if not role:
            logger.error(f"Role ID {assignment.role_id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
            
        # Business Logic 2: Prevent unassignment from default role
        if role.is_default:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot unassign users from default role"
            )
            
        # Business Logic 3: Verify default role exists
        default_role = self.role_repository.get_default_role()
        if not default_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Default role not found. Cannot reassign users."
            )
        
        # Business Logic 4: Validate users
        errors = []
        valid_user_ids = []
        for user_id in assignment.user_ids:
            user = self.user_repository.get_user(user_id)
            if not user:
                errors.append(FailedAssignment(user_id=user_id, reason="User not found").dict())
                continue
            if not user.is_verified:
                errors.append(FailedAssignment(user_id=user_id, reason="User not verified").dict())
                continue
            if not user.is_active:
                errors.append(FailedAssignment(user_id=user_id, reason="User not active").dict())
                continue
            if user.role_id != assignment.role_id:
                errors.append(FailedAssignment(user_id=user_id, reason="User not assigned to this role").dict())
                continue
            valid_user_ids.append(user_id)
        
        # Business Logic 5: Unassign valid users from the role
        if valid_user_ids:
            if not self.role_repository.remove_users_from_role(assignment.role_id, valid_user_ids):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to unassign users from role"
                )
        
        # Business Logic 6: Handle response based on errors and valid unassignments
        if errors and valid_user_ids:
            return UserUnassignmentResult(
                failed_unassignments=errors,
                **self.role_repository.get_role(assignment.role_id).dict()
            )
        elif errors and not valid_user_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=errors
            )
        
        return self.role_repository.get_role(assignment.role_id)