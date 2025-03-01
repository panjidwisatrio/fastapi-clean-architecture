from sqlalchemy.orm import Session
from app.core.logging import setup_logger, log_operation
from app.models.role import Role
from app.models.permission_role import PermissionRole
from app.schemas.role import RoleCreate

logger = setup_logger("role_repositories")

class RoleRepository:
    def __init__(self, db: Session):
        self.db = db
    
    @log_operation(logger)
    def get_role(self, role_id: int) -> Role:
        return self.db.query(Role).filter(Role.id == role_id).first()

    @log_operation(logger)
    def get_role_by_name(self, role_name: str) -> Role:
        return self.db.query(Role).filter(Role.role_name == role_name).first()

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
    def delete_role(self, role_id: int) -> Role:
        db_role = self.get_role(role_id)
        if db_role:
            self.db.delete(db_role)
            self.db.commit()
        return db_role
    
    @log_operation(logger)
    def add_permission_to_role(self, role_id: int, permission_id: int) -> Role:
        db_role = self.get_role(role_id)
        if not db_role:
            return None
            
        # Check if the permission already exists for this role
        existing = self.db.query(PermissionRole).filter(
            PermissionRole.role_id == role_id,
            PermissionRole.permission_id == permission_id
        ).first()
        
        if not existing:
            role_permission = PermissionRole(roles_id=role_id, permission_id=permission_id)
            self.db.add(role_permission)
            self.db.commit()
            
        return self.get_role(role_id)
        
    @log_operation(logger)
    def remove_permission_from_role(self, role_id: int, permission_id: int) -> Role:
        db_role = self.get_role(role_id)
        if not db_role:
            return None
            
        role_permission = self.db.query(PermissionRole).filter(
            PermissionRole.role_id == role_id,
            PermissionRole.permission_id == permission_id
        ).first()
        
        if role_permission:
            self.db.delete(role_permission)
            self.db.commit()
            
        return self.get_role(role_id)
