#!/usr/bin/env python3
"""Module to initiate initial data and permissions."""
from pathlib import Path
import json
import sys

try:
    from ..util import find_project_root
except ImportError:
    project_root_path = Path(__file__).parent.parent.parent
    sys.path.append(str(project_root_path))
    from module.util import find_project_root

def initiate_initial_data(project_root: Path):
    """Initialize initial data file with super admin template"""
    try:
        file_path = project_root / Path("app/data/initial_data.json")
        
        # Create initial data file if it doesn't exist
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created directory: {file_path.parent}")
         
        # Prompt for overwrite if file exists
        is_continue = input("⚠️  initial_data.json already exists. Overwrite? (y/n): ") if file_path.exists() else 'y'
        if file_path.exists() and is_continue.lower() != 'y':
            print("❌ Initialization cancelled by user")
            sys.exit(0)
        
        json_content = {
            "super_admin": {
                "first_name": "<first_name>",
                "last_name": "<last_name>",
                "email": "<email@example.com>",
                "password": "<password>"
            }
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_content, f, indent=4)
        
        print(f"✓ Generated: app/data/initial_data.json")
        
    except PermissionError:
        print(f"❌ Error: Permission denied when writing to {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error creating initial data: {str(e)}")
        sys.exit(1)
    

def initiate_permissions(project_root: Path):
    """Initialize permissions file with default roles and scopes"""
    try:
        file_path = project_root / Path("app/data/permissions.json")
        
        # Create permissions file if it doesn't exist
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created directory: {file_path.parent}")
            
        # Prompt for overwrite if file exists
        is_continue = input("⚠️  permissions.json already exists. Overwrite? (y/n): ") if file_path.exists() else 'y'
        if file_path.exists() and is_continue.lower() != 'y':
            print("❌ Initialization cancelled by user")
            sys.exit(0)
        
        json_content = {
            "scopes": {
                "manage_permissions": "manage permissions",
                "view_permissions": "view permissions",
                "manage_roles": "manage roles",
                "view_roles": "view roles",
                "create_user": "create user",
                "get_users": "get users",
                "get_user_by_id": "get user by id",
                "update_user": "update user",
                "deactivate_user": "deactivate user"
            },
            "roles": {
                "Super Admin": {
                    "description": "Super Admin has all permissions",
                    "permissions": [
                        "manage_permissions",
                        "view_permissions",
                        "manage_roles",
                        "view_roles",
                        "create_user",
                        "get_users",
                        "get_user_by_id",
                        "update_user",
                        "deactivate_user"
                    ]
                },
                "Admin": {
                    "description": "Admin can manage users and view data",
                    "permissions": [
                        "create_user",
                        "get_users",
                        "get_user_by_id",
                        "update_user",
                        "deactivate_user"
                    ]
                },
                "User": {
                    "description": "Regular user with basic permissions",
                    "permissions": []
                }
            }
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_content, f, indent=4)
        
        print(f"✓ Generated: app/data/permissions.json")
        
    except PermissionError:
        print(f"❌ Error: Permission denied when writing to {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error creating permissions: {str(e)}")
        sys.exit(1)


def verify_initialization(project_root: Path):
    """Verify json schemas of the initialized files"""
    initial_data_path = project_root / Path("app/data/initial_data.json")
    permissions_path = project_root / Path("app/data/permissions.json")
    
    # Add verification logic here
    try:
        # Verify initial_data.json
        if not initial_data_path.exists():
            print(f"❌ Verification failed: {initial_data_path} does not exist")
            return False
        
        with open(initial_data_path, 'r', encoding='utf-8') as f:
            initial_data = json.load(f)
        
        # Validate initial_data schema
        if "super_admin" not in initial_data:
            print("❌ Verification failed: 'super_admin' key missing in initial_data.json")
            return False
        
        required_admin_fields = ["first_name", "last_name", "email", "password"]
        for field in required_admin_fields:
            if field not in initial_data["super_admin"]:
                print(f"❌ Verification failed: '{field}' missing in super_admin")
                return False
        
        default_values = ["<first_name>", "<last_name>", "<email>", "<password>"]
        for field, default in zip(required_admin_fields, default_values):
            if initial_data["super_admin"].get(field) == default:
                print(f"⚠️  Warning: '{field}' in super_admin still has default placeholder value")
        
        print("✓ initial_data.json schema is valid")
        
        # Verify permissions.json
        if not permissions_path.exists():
            print(f"❌ Verification failed: {permissions_path} does not exist")
            return False
        
        with open(permissions_path, 'r', encoding='utf-8') as f:
            permissions = json.load(f)
        
        # Validate permissions schema
        if "scopes" not in permissions:
            print("❌ Verification failed: 'scopes' key missing in permissions.json")
            return False
        
        if "roles" not in permissions:
            print("❌ Verification failed: 'roles' key missing in permissions.json")
            return False
        
        # Validate roles structure
        for role_name, role_data in permissions["roles"].items():
            if "description" not in role_data:
                print(f"❌ Verification failed: 'description' missing for role '{role_name}'")
                return False
            if "permissions" not in role_data:
                print(f"❌ Verification failed: 'permissions' missing for role '{role_name}'")
                return False
            if not isinstance(role_data["permissions"], list):
                print(f"❌ Verification failed: 'permissions' must be a list for role '{role_name}'")
                return False
        
        print("✓ permissions.json schema is valid")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Verification failed: Invalid JSON format - {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        return False


def main():
    """Main function to initialize all data files"""
    print("\n🚀 Initializing project data files...\n")
    
    try:
        project_root = find_project_root()
        
        # Initiate initial data
        initiate_initial_data(project_root)
        
        # Initiate permissions
        initiate_permissions(project_root)
        
        # Verify initialization
        is_valid = verify_initialization(project_root)
        if not is_valid:
            print("\n❌ Initialization verification failed. Please check the above errors.")
            sys.exit(1)
        
        print("\n✅ Data initialization completed!")
        print("\n📚 Next steps:")
        print("1. Edit app/data/initial_data.json with your super admin credentials")
        print("2. Review app/data/permissions.json and add custom permissions if needed")
        print("3. Run the database initialization script to seed the data")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Initialization cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Initialization failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()