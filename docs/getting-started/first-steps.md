# First Steps

Get started with the FastAPI Clean Architecture by making your first API requests.

## Prerequisites

Before proceeding, ensure you have completed:

- [x] [Installation](installation.md)
- [x] [Configuration](configuration.md)
- [x] [Data Setup](data-setup.md)
- [x] [Database Migrations](../database/migrations.md)

## Start the Application

Run the development server:

```bash
uvicorn app.main:app --reload
```

You should see output like:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:app:Application starting in development environment
INFO:app:Initializing database on startup
INFO:app:Database initialization completed
INFO:     Application startup complete.
```

## Access API Documentation

Open your browser and navigate to:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

The Swagger UI provides an interactive interface to test all API endpoints!

## Your First API Request

### 1. Login as Super Admin

Using the super admin credentials from `app/data/initial_data.json`:

=== "Swagger UI"
    1. Navigate to [http://localhost:8000/docs](http://localhost:8000/docs)
    2. Find `POST /auth/login`
    3. Click "Try it out"
    4. Enter your credentials:
       ```json
       {
         "username": "admin@example.com",
         "password": "Admin@123456"
       }
       ```
    5. Click "Execute"

=== "cURL"
    ```bash
    curl -X POST "http://localhost:8000/auth/login" \
      -H "Content-Type: application/json" \
      -d '{
        "username": "admin@example.com",
        "password": "Admin@123456"
      }'
    ```

=== "Python"
    ```python
    import requests

    response = requests.post(
        "http://localhost:8000/auth/login",
        json={
            "email": "admin@example.com",
            "password": "Admin@123456"
        }
    )
    
    data = response.json()
    access_token = data["access_token"]
    print(f"Token: {access_token}")
    ```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

Copy the `access_token` for subsequent requests!

### 2. Authorize in Swagger UI

To use protected endpoints in Swagger UI:

1. Click the **"Authorize"** button (top right with lock icon)
2. Enter your email in `username` field and password in `password` field
3. Click "Authorize"
4. Click "Close"

Now you can access protected endpoints!

### 3. Get Your Profile

=== "Swagger UI"
    1. Find `GET /me`
    2. Click "Try it out"
    3. Click "Execute"

=== "cURL"
    ```bash
    curl -X GET "http://localhost:8000/me" \
      -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
    ```

=== "Python"
    ```python
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(
        "http://localhost:8000/me",
        headers=headers
    )
    
    print(response.json())
    ```

Response:

```json
{
  "email": "admin@example.com",
  "first_name": "Super",
  "last_name": "Admin",
  "id": 1,
  "role_id": 1,
  "is_verified": true,
  "is_active": true,
  "last_active": "2025-11-19T04:57:16.593Z",
  "created_at": "2025-11-19T04:57:16.593Z",
  "updated_at": "2025-11-19T04:57:16.593Z",
  "role": {
    "role_name": "Super Admin",
    "id": 1,
    "created_at": "2025-11-19T04:57:16.593Z",
    "updated_at": "2025-11-19T04:57:16.593Z",
    "permissions": []
  }
}
```

### 4. List All Users

=== "Swagger UI"
    1. Find `GET /users`
    2. Click "Try it out"
    3. Optionally set `skip` and `limit` for pagination
    4. Click "Execute"

=== "cURL"
    ```bash
    curl -X GET "http://localhost:8000/users?skip=0&limit=10" \
      -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
    ```

Response:

```json
[
  {
    "email": "admin@example.com",
    "first_name": "Super",
    "last_name": "Admin",
    "id": 1,
    "role_id": 1,
    "is_verified": true,
    "is_active": true,
    "last_active": "2025-11-19T04:59:13.895Z",
    "created_at": "2025-11-19T04:59:13.895Z",
    "updated_at": "2025-11-19T04:59:13.895Z",
    "role": {
      "role_name": "Super Admin",
      "id": 1,
      "created_at": "2025-11-19T04:59:13.895Z",
      "updated_at": "2025-11-19T04:59:13.895Z",
      "permissions": []
    }
  }
]
```

### 5. Create a New User

=== "Swagger UI"
    1. Find `POST /users`
    2. Click "Try it out"
    3. Enter user data:
       ```json
       {
         "first_name": "John",
         "last_name": "Doe",
         "email": "john@example.com",
         "roles_id": 3
       }
       ```
    4. Click "Execute"

=== "cURL"
    ```bash
    curl -X POST "http://localhost:8000/users" \
      -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "roles_id": 3
      }'
    ```

Response:

```json
{
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "id": 2,
  "role_id": 3,
  "is_verified": true,
  "is_active": true,
  "last_active": "2025-11-19T05:00:03.405Z",
  "created_at": "2025-11-19T05:00:03.405Z",
  "updated_at": "2025-11-19T05:00:03.405Z",
  "role": {
    "role_name": "User",
    "id": 3,
    "created_at": "2025-11-19T05:00:03.405Z",
    "updated_at": "2025-11-19T05:00:03.405Z",
    "permissions": []
  }
}
```

## Common Tasks

### Register a New User (Public)

Anyone can register without authentication:

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!"
  }'
```

### Update Your Profile

```bash
curl -X PUT "http://localhost:8000/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Updated",
    "last_name": "Name",
    "email": "updated@example.com"
  }'
```

### Change Your Password

```bash
curl -X PUT "http://localhost:8000/me/password" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "Admin@123456",
    "new_password": "NewSecurePass789!",
    "password_confirm": "NewSecurePass789!"
  }'
```

### List All Roles

```bash
curl -X GET "http://localhost:8000/roles?skip=0&limit=100" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Logout

```bash
curl -X POST "http://localhost:8000/auth/logout" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Testing with Postman

1. **Import Collection**:
   - Head to `/openapi.json` in your running app (e.g., [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json))
   - Download the JSON file
   - Import into Postman

2. **Set Environment Variables**:
   - `base_url`: `http://localhost:8000`
   - `access_token`: Your JWT token

3. **Configure Authorization**:
   - Type: Bearer Token
   - Token: `{{access_token}}`

## Next Steps

Now that you're familiar with the basics:

- **Learn about the Architecture**: [Architecture Overview](../architecture/overview.md)
- **Explore API Endpoints**: [API Documentation](../api/overview.md)
- **Generate Your Own CRUD**: [Code Generation](../development/code-generation.md)
- **Deploy to Production**: [Production Guide](../deployment/production.md)

## Troubleshooting

### 401 Unauthorized

**Problem:** All protected endpoints return 401

**Solution:**

- Ensure you're sending the Authorization header
- Check token format: `Bearer your_token_here`
- Token may have expired (default 30 minutes)
- Login again to get a new token

### 403 Forbidden

**Problem:** Endpoint returns "Not enough permissions"

**Solution:**

- Your user lacks required permissions
- Check your role in GET /me
- Verify permissions in `app/data/permissions.json`
- May need Super Admin or Admin role

### Connection Refused

**Problem:** Cannot connect to http://localhost:8000

**Solution:**

- Ensure server is running: `uvicorn app.main:app --reload`
- Check for errors in server logs
- Verify port 8000 is not in use
- Try: `http://127.0.0.1:8000`

## Quick Reference

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/auth/register` | POST | No | Register new user |
| `/auth/login` | POST | No | Login and get token |
| `/auth/logout` | POST | Yes | Logout (blacklist token) |
| `/me` | GET | Yes | Get current user profile |
| `/me` | PUT | Yes | Update profile |
| `/me/password` | PUT | Yes | Change password |
| `/users` | GET | Yes | List all users (Admin) |
| `/users` | POST | Yes | Create user (Admin) |
| `/users/{id}` | GET | Yes | Get user by ID |
| `/users/{id}` | PUT | Yes | Update user (Admin) |
| `/roles` | GET | Yes | List all roles |
| `/permissions` | GET | Yes | List all permissions |

For complete API documentation, visit [http://localhost:8000/docs](http://localhost:8000/docs)
