import json
import os
from app.core.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.permission_role import PermissionRole
from app.core.utils import get_password_hash, load_permissions

def init_db(logger):
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Load permissions data from JSON
        permissions_data = load_permissions()
        
        # Initialize permissions
        permission_map = {}
        for scope_name, scope_description in permissions_data["scopes"].items():
            # Check if permission already exists
            permission = db.query(Permission).filter(Permission.permission_name == scope_name).first()
            if not permission:
                permission = Permission(permission_name=scope_name, description=scope_description)
                db.add(permission)
                db.flush()
                logger.info(f"Created permission: {scope_name}")
            permission_map[scope_name] = permission

        # Initialize roles with their permissions
        role_objects = {}
        for role_name, role_info in permissions_data["roles"].items():
            # Check if role already exists
            role = db.query(Role).filter(Role.role_name == role_name).first()
            if not role:
                role = Role(role_name=role_name, description=role_info["description"])
                db.add(role)
                db.flush()
                logger.info(f"Created role: {role_name}")
            
            role_objects[role_name] = role
            
            # Assign permissions to role
            existing_permissions = {rp.permission_id for rp in db.query(PermissionRole).filter(PermissionRole.role_id == role.id).all()}
            
            for perm_name in role_info["permissions"]:
                perm = permission_map.get(perm_name)
                if perm and perm.id not in existing_permissions:
                    role_permission = PermissionRole(role_id=role.id, permission_id=perm.id)
                    db.add(role_permission)
                    logger.info(f"Added permission {perm_name} to role {role_name}")
        
        # Create a super admin user if it doesn't exist
        super_admin_role = role_objects.get("Super Admin")
        if super_admin_role:
            # Check if any super admin user already exists
            existing_super_admin = db.query(User).filter(User.role_id == super_admin_role.id).first()
            
            if not existing_super_admin:
                with open(os.path.join("app", "data", "initial_data.json")) as f:
                    super_admin_data = json.load(f)["super_admin"]
                    
                    super_admin = User(
                        role_id=super_admin_role.id,
                        first_name=super_admin_data["first_name"],
                        last_name=super_admin_data["last_name"],
                        email=super_admin_data["email"],
                        hashed_password=get_password_hash(super_admin_data["password"]),
                        is_verified=True,
                        is_active=True
                    )
                    db.add(super_admin)
                    logger.info(f"Created super admin user: {super_admin_data['email']}")
            else:
                logger.info(f"Super admin user already exists: {existing_super_admin.email}")
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error initializing database: {str(e)}")
        raise
    finally:
        db.close()
