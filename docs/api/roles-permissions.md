# Roles & Permissions API

API for managing Role-Based Access Control (RBAC).

## Roles

### Create Role
```http
POST /roles/
```

### List Roles
```http
GET /roles/
```

### Get Role
```http
GET /roles/{id}
```

### Delete Role
```http
DELETE /roles/{id}
```

## Permissions

### Assign Permission to Role
```http
POST /roles/{role_id}/permissions/{permission_id}
```

### Remove Permission from Role
```http
DELETE /roles/{role_id}/permissions/{permission_id}
```

All endpoints require authentication and appropriate permissions (`manage_roles`, `view_roles`).
