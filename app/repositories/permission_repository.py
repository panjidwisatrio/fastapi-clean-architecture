from sqlalchemy.orm import Session
from app.core.logging import setup_logger, log_operation
from app.models.permission import Permission
from app.schemas.permission import PermissionCreate

logger = setup_logger("permission_repositories")

class PermissionRepository:
    def __init__(self, db: Session):
        self.db = db
    
    @log_operation(logger)
    def get_permission(self, permission_id: int) -> Permission:
        return self.db.query(Permission).filter(Permission.id == permission_id).first()

    @log_operation(logger)
    def get_permission_by_name(self, permission_name: str) -> Permission:
        return self.db.query(Permission).filter(Permission.permission_name == permission_name).first()

    @log_operation(logger)
    def get_permissions(self, skip: int = 0, limit: int = 100) -> list[Permission]:
        return self.db.query(Permission).offset(skip).limit(limit).all()

    @log_operation(logger)
    def create_permission(self, permission: PermissionCreate) -> Permission:
        db_permission = Permission(permission_name=permission.permission_name)
        self.db.add(db_permission)
        self.db.commit()
        self.db.refresh(db_permission)
        return db_permission

    @log_operation(logger)
    def delete_permission(self, permission_id: int) -> Permission:
        db_permission = self.get_permission(permission_id)
        if db_permission:
            self.db.delete(db_permission)
            self.db.commit()
        return db_permission
