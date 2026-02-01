from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.logging import setup_logger, log_operation
from app.models.role import Role
from app.models.permission_role import PermissionRole
from app.models.user import User
from app.schemas.role import RoleCreate, RoleUpdate

logger = setup_logger("role_repositories")

class RoleRepository:
    def __init__(self, db: Session):
        self.db = db
    
    @log_operation(logger)
    def get_role(self, role_id: int) -> Role:
        return self.db.query(Role).filter(Role.id == role_id).first()

    @log_operation(logger)
    def get_default_role(self) -> Role:
        return self.db.query(Role).filter(Role.is_default == 1).first()
    
    @log_operation(logger)
    def get_role_by_name(self, role_name: str) -> Role:
        return self.db.query(Role).filter(func.lower(Role.role_name) == role_name.lower()).first()

    @log_operation(logger)
    def get_roles(self, skip: int = 0, limit: int = 100) -> list[Role]:
        return self.db.query(Role).offset(skip).limit(limit).all()

    @log_operation(logger)
    def create_role(self, role: RoleCreate) -> Role:
        db_role = Role(role_name=role.role_name)
        self.db.add(db_role)
        self.db.commit()
        self.db.refresh(db_role)
        return db_role
    
    @log_operation(logger)
    def update_role(self, role_id: int, role: RoleUpdate) -> Role:
        db_role = self.get_role(role_id)
        if not db_role:
            return None
        db_role.role_name = role.role_name
        self.db.commit()
        self.db.refresh(db_role)
        return db_role

    @log_operation(logger)
    def delete_role(self, role_id: int) -> Role:
        db_role = self.get_role(role_id)
        if db_role:
            self.db.delete(db_role)
            self.db.commit()
        return db_role
    
    @log_operation(logger)
    def validate_permissions_exist(self, role_id: int, permission_ids: List[int]) -> List[PermissionRole]:
        existing_permissions = self.db.query(PermissionRole).filter(
            PermissionRole.role_id == role_id,
            PermissionRole.permission_id.in_(permission_ids)
        ).all()
        return existing_permissions
    
    @log_operation(logger)
    def add_permission_to_role(self, role_id: int, permission_ids: List[int]) -> Role:
        db_role = self.get_role(role_id)
        if not db_role:
            return None
        
        for pid in permission_ids:
            role_permission = PermissionRole(role_id=role_id, permission_id=pid)
            self.db.add(role_permission)
        self.db.commit()
        
        return db_role
        
    @log_operation(logger)
    def remove_permission_from_role(self, role_id: int, permission_ids: List[int]) -> Role:
        db_role = self.get_role(role_id)
        if not db_role:
            return None
            
        for pid in permission_ids:
            role_permission = PermissionRole(role_id=role_id, permission_id=pid)
            if role_permission:
                self.db.delete(role_permission)
        self.db.commit()
        
        return db_role
    
    @log_operation(logger)
    def add_users_to_role(self, role_id: int, user_ids: List[int]) -> Role:
        # Implementation to add users to role
        db_role = self.get_role(role_id)
        if not db_role:
            return None
        
        # Bulk update users' role_id
        self.db.query(User).filter(User.id.in_(user_ids)).update({"role_id": role_id}, synchronize_session=False)
        self.db.commit()
        
        return db_role
    
    @log_operation(logger)
    def remove_users_from_role(self, role_id: int, user_ids: List[int]) -> Role:
        # Implementation to remove users from role
        db_role = self.get_role(role_id)
        if not db_role:
            return None
        
        # Get default role to assign users to
        default_role = self.db.query(Role).filter(Role.is_default == 1).first()
        
        # Bulk update users' role_id to default role
        self.db.query(User).filter(User.id.in_(user_ids)).update({"role_id": default_role.id}, synchronize_session=False)
        self.db.commit()
        
        return db_role
    
    @log_operation(logger)
    def set_role_as_default(self, role_id: int) -> Role:
        # Unset previous default role
        self.db.query(Role).filter(Role.is_default == 1).update({"is_default": 0}, synchronize_session=False)
        
        # Set new default role
        db_role = self.get_role(role_id)
        if not db_role:
            return None
        
        db_role.is_default = 1
        self.db.commit()
        self.db.refresh(db_role)
        
        return db_role