# Data Setup

Learn how to configure initial data files for roles, permissions, and admin users.

## Overview

Before running the application, you need to prepare initial data files in the `app/data/` directory. These files seed the database with:

- Initial roles and permissions
- Super admin user credentials

## Required Files

1. `app/data/initial_data.json` - Super admin user credentials
2. `app/data/permissions.json` - Roles and permissions definitions

## 1. Super Admin Configuration

### Create `initial_data.json`

Create or edit `app/data/initial_data.json`:

```json
{
  "super_admin": {
    "first_name": "Super",
    "last_name": "Admin",
    "email": "admin@example.com",
    "password": "Admin@123456"
  }
}
```

### JSON Schema

```json
{
  "super_admin": {
    "first_name": "string",      // First name
    "last_name": "string",        // Last name
    "email": "string (email)",    // Valid email address
    "password": "string"          // Will be hashed automatically
  }
}
```

!!! danger "Security"
    - Change default credentials before production!
    - Use strong passwords (min 12 characters)
    - Password will be hashed before storing

## 2. Permissions Configuration

### Create `permissions.json`

Create or edit `app/data/permissions.json`:

```json
{
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
```

### JSON Schema

```json
{
  "scopes": {
    "permission_key": "Human readable description",
    // Add more permissions...
  },
  "roles": {
    "Role Name": {
      "description": "Role description",
      "permissions": ["perm1", "perm2"]  // Array of permission keys
    }
    // Add more roles...
  }
}
```

## Adding Custom Permissions

### Example: Blog Management System

```json
{
  "scopes": {
    "create_post": "Create new blog post",
    "edit_post": "Edit existing blog post",
    "delete_post": "Delete blog post",
    "publish_post": "Publish blog post",
    "view_analytics": "View website analytics"
  },
  "roles": {
    "Content Creator": {
      "description": "Can create and edit posts",
      "permissions": [
        "create_post",
        "edit_post"
      ]
    },
    "Editor": {
      "description": "Can create, edit, and publish posts",
      "permissions": [
        "create_post",
        "edit_post",
        "publish_post"
      ]
    },
    "Publisher": {
      "description": "Full control over content",
      "permissions": [
        "create_post",
        "edit_post",
        "delete_post",
        "publish_post",
        "view_analytics"
      ]
    }
  }
}
```

## Validation

### Pre-flight Checklist

Before starting the application:

- [ ] `app/data/initial_data.json` exists
- [ ] `app/data/permissions.json` exists
- [ ] Super admin email is valid format
- [ ] All permission keys in roles exist in scopes
- [ ] Password meets security requirements
- [ ] Email domain is in `ACCEPTED_EMAIL_DOMAINS`

### Validate JSON Files (Optional)

Create a validation script `validate_data.py`:

```python
import json
import sys

def validate_initial_data():
    try:
        with open('app/data/initial_data.json', 'r') as f:
            data = json.load(f)
        
        # Check structure
        if "super_admin" not in data:
            print("✗ Missing 'super_admin' key")
            return False
        
        # Check required fields
        required = ["first_name", "last_name", "email", "password"]
        admin = data["super_admin"]
        
        for field in required:
            if field not in admin:
                print(f"✗ Missing '{field}' in super_admin")
                return False
        
        # Validate email
        if "@" not in admin["email"]:
            print(f"✗ Invalid email: {admin['email']}")
            return False
        
        print("✓ initial_data.json is valid")
        return True
    
    except FileNotFoundError:
        print("✗ initial_data.json not found!")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ JSON syntax error: {e}")
        return False

def validate_permissions():
    try:
        with open('app/data/permissions.json', 'r') as f:
            data = json.load(f)
        
        # Check structure
        if "scopes" not in data or "roles" not in data:
            print("✗ Missing 'scopes' or 'roles' key")
            return False
        
        # Validate role permissions
        scopes = data["scopes"]
        for role_name, role_data in data["roles"].items():
            if "permissions" not in role_data:
                print(f"✗ Role '{role_name}' missing 'permissions'")
                return False
            
            for perm in role_data["permissions"]:
                if perm not in scopes:
                    print(f"✗ Permission '{perm}' not in scopes")
                    return False
        
        print("✓ permissions.json is valid")
        return True
    
    except FileNotFoundError:
        print("✗ permissions.json not found!")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ JSON syntax error: {e}")
        return False

if __name__ == "__main__":
    print("Validating data files...\n")
    
    valid1 = validate_initial_data()
    print()
    valid2 = validate_permissions()
    
    print("\n" + "="*50)
    if valid1 and valid2:
        print("✓ All data files are valid!")
        sys.exit(0)
    else:
        print("✗ Some files have errors. Fix them before running the app.")
        sys.exit(1)
```

Run validation:

```bash
python validate_data.py
```

## Database Initialization

When you start the application for the first time, it will automatically:

1. Load permissions from `permissions.json`
2. Create roles with associated permissions
3. Create super admin user from `initial_data.json`

Check the logs on startup:

```
INFO:app:Application starting in development environment
INFO:app:Initializing database on startup
INFO:app:Created permission: create_user
INFO:app:Created role: Super Admin
INFO:app:Added permission create_user to role Super Admin
INFO:app:Created super admin user: admin@example.com
INFO:app:Database initialization completed
```

## Best Practices

### Security

✅ **DO:**

- Change default credentials immediately
- Use strong passwords (12+ characters, mixed case, numbers, symbols)
- Restrict email domains in production
- Rotate secrets regularly
- Never commit real credentials to Git

❌ **DON'T:**

- Use default passwords in production
- Share admin credentials
- Use weak passwords
- Commit `.env` files with real credentials

### Permission Design

✅ **DO:**

- Use descriptive permission names
- Follow naming convention: `verb_noun` (e.g., `create_user`)
- Group related permissions
- Document permission purposes
- Consider role hierarchy

❌ **DON'T:**

- Create duplicate permissions
- Use vague permission names
- Give users unnecessary permissions
- Mix different concerns in one permission

## Troubleshooting

### Super Admin Cannot Login

**Problem:** Login fails with valid credentials

**Solutions:**

- Check email domain is in `ACCEPTED_EMAIL_DOMAINS`
- Verify database was initialized (check logs)
- Try deleting database and restarting (dev only)
- Check password is correct (case-sensitive)

### Permission Not Found Errors

**Problem:** `KeyError` or permission errors on startup

**Solutions:**

- Verify `permissions.json` is valid JSON
- Ensure all permission keys in roles exist in scopes
- Check for typos in permission names
- Run validation script

### File Not Found Errors

**Problem:** `FileNotFoundError` on startup

**Solutions:**

- Ensure files exist in `app/data/` directory
- Check file names are exactly `initial_data.json` and `permissions.json`
- Verify file paths in logs

## What's Next?

After setting up data files:

- [Database Migrations](../database/migrations.md) - Set up database schema
- [First Steps](first-steps.md) - Make your first API request
- [API Authentication](../api/authentication.md) - Learn about auth endpoints
