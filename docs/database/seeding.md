# Database Seeding

Initial data setup and seed data management.

## Data Files

### permissions.json

Defines roles and permissions:

```json
{
  "scopes": {
    "user:read": "Read user information",
    "user:create": "Create new users"
  },
  "roles": {
    "Super Admin": {
      "description": "Full system access",
      "permissions": ["user:read", "user:create"]
    }
  }
}
```

### initial_data.json

Defines super admin user:

```json
{
  "super_admin": {
    "first_name": "Admin",
    "last_name": "User",
    "email": "admin@example.com",
    "password": "changeme"
  }
}
```

## Automatic Seeding

On first application start, `app/core/init_db.py` automatically:

1. Loads permissions from `permissions.json`
2. Creates roles and assigns permissions
3. Creates super admin user from `initial_data.json`

## Manual Seeding

Run database initialization manually:

```bash
python -c "from app.core.init_db import init_db; init_db()"
```

See [Data Setup Guide](../getting-started/data-setup.md) for configuration details.
