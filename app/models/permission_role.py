from sqlalchemy import Column, Integer, ForeignKey
from app.core.database import Base

class PermissionRole(Base):
    __tablename__ = "permission_roles"

    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permissions.id"), primary_key=True)