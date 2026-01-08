# API Overview

Comprehensive overview of the REST API endpoints available in FastAPI Clean Architecture.

## Introduction

This project provides a RESTful API built with FastAPI, featuring JWT authentication, role-based access control (RBAC), and comprehensive user management capabilities.

## Base URL

```
# Development
http://127.0.0.1:8000

# Production
https://your-domain.com
```

## API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`
- **OpenAPI Schema**: `http://127.0.0.1:8000/openapi.json`

## Authentication

Most endpoints require authentication using JWT (JSON Web Tokens).

### Authentication Flow

1. Register or login to get access token
2. Include token in `Authorization` header for protected endpoints
3. Refresh token when access token expires

### Header Format

```http
Authorization: Bearer <your_access_token>
```

## Endpoint Categories

### 1. Authentication

Endpoints for user authentication and account management.

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | ❌ |
| POST | `/auth/login` | Login and get tokens | ❌ |
| POST | `/auth/logout` | Logout (invalidate token) | ✅ |
| POST | `/auth/forgot-password` | Request password reset | ❌ |
| POST | `/auth/verify-forgot-password-otp` | Verify OTP for password reset | ❌ |

[View Details →](authentication.md)

### 2. User Management

Endpoints for managing users (CRUD operations).

| Method | Endpoint | Description | Auth Required | Permission |
|--------|----------|-------------|---------------|------------|
| GET | `/users/` | List all users | ✅ | `get_users` |
| GET | `/users/{id}` | Get user by ID | ✅ | `get_user_by_id` |
| POST | `/users/` | Create new user | ✅ | `create_user` |
| PUT | `/users/{id}` | Update user | ✅ | `update_user` |
| DELETE | `/users/{id}` | Deactivate user | ✅ | `deactivate_user` |

[View Details →](users.md)

### 3. Current User (Me)

Endpoints for the authenticated user to manage their own profile.

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/me/` | Get current user profile | ✅ |
| PUT | `/me/` | Update current user profile | ✅ |
| PUT | `/me/password` | Update current user password | ✅ |
| DELETE | `/me/` | Deactivate current user account | ✅ |

[View Details →](users.md#current-user-endpoints)

### 4. Role Management

Endpoints for managing roles and RBAC.

| Method | Endpoint | Description | Auth Required | Permission |
|--------|----------|-------------|---------------|------------|
| GET | `/roles/` | List all roles | ✅ | `view_roles` |
| GET | `/roles/{id}` | Get role by ID | ✅ | `view_roles` |
| POST | `/roles/` | Create new role | ✅ | `manage_roles` |
| PUT | `/roles/{id}` | Update role | ✅ | `manage_roles` |
| DELETE | `/roles/{id}` | Delete role | ✅ | `manage_roles` |
[View Details →](roles-permissions.md)

### 5. Permission Management

Endpoints for managing permissions.

| Method | Endpoint | Description | Auth Required | Permission |
|--------|----------|-------------|---------------|------------|
| GET | `/permissions/` | List all permissions | ✅ | `permission:read` |
| GET | `/permissions/{id}` | Get permission by ID | ✅ | `permission:read` |
| POST | `/permissions/` | Create permission | ✅ | `permission:create` |
| PUT | `/permissions/{id}` | Update permission | ✅ | `permission:update` |
| DELETE | `/permissions/{id}` | Delete permission | ✅ | `permission:delete` |
| POST | `/roles/{id}/permissions/{permission_id}` | Assign permissions to role | ✅ | `role:update` |

[View Details →](roles-permissions.md)

### 6. OTP (One-Time Password)

Endpoints for OTP-based verification.

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/otp/request` | Send OTP to email | ❌ |
| POST | `/otp/verify` | Verify OTP code | ❌ |

[View Details →](otp.md)

## Common Response Formats

### Success Response

```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Error Response

```json
{
  "detail": "Error message here"
}
```

### Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### List Response (Paginated)

```json
{
  "items": [
    {"id": 1, "email": "user1@example.com"},
    {"id": 2, "email": "user2@example.com"}
  ],
  "total": 25,
  "page": 1,
  "size": 10,
  "pages": 3
}
```

## HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request succeeded with no response body |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required or failed |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |

## Pagination

List endpoints support pagination using query parameters:

```http
GET /api/users?skip=0&limit=10
```

**Parameters:**

- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Maximum number of records to return (default: 100, max: 100)

**Example:**

```bash
# Get first 10 users
curl "http://127.0.0.1:8000/users/?skip=0&limit=10"

# Get next 10 users
curl "http://127.0.0.1:8000/users/?skip=10&limit=10"
```

## Filtering and Sorting

Some endpoints support filtering and sorting:

```http
GET /users/?is_active=true&sort_by=created_at&order=desc
```

**Common Parameters:**

- `is_active` (bool): Filter by active status
- `search` (string): Search in multiple fields
- `sort_by` (string): Field to sort by
- `order` (string): `asc` or `desc`

## Rate Limiting

!!! warning "Production"
    In production, consider implementing rate limiting to prevent abuse.

Recommended limits:
- Authentication endpoints: 5 requests/minute
- General endpoints: 100 requests/minute
- Public endpoints: 10 requests/minute

## CORS

The API supports Cross-Origin Resource Sharing (CORS) for web applications.

**Configuration** (`.env`):

```env
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend.com
```

## API Versioning

Currently using path-based versioning (implicit v1).

Future versions will use:

```
/api/v2/users
/api/v2/auth
```

## Quick Start Examples

### Example 1: Register and Login

```bash
# 1. Register new user
curl -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123!",
    "full_name": "New User"
  }'

# Response:
# {
#   "id": 42,
#   "email": "newuser@example.com",
#   "full_name": "New User",
#   "is_active": true,
#   "is_verified": false
# }

# 2. Login
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123!"
  }'

# Response:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer"
# }
```

### Example 2: Make Authenticated Request

```bash
# Get current user profile
curl -X GET "http://127.0.0.1:8000/me/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Response:
# {
#   "id": 42,
#   "email": "newuser@example.com",
#   "full_name": "New User",
#   "is_active": true,
#   "is_verified": false,
#   "role": {
#     "id": 2,
#     "name": "User"
#   }
# }
```

### Example 3: Using Swagger UI

1. Go to `http://127.0.0.1:8000/docs`
2. Click **"Authorize"** button (top right)
3. Enter: `Bearer <your_access_token>`
4. Click **"Authorize"** then **"Close"**
5. Now you can try any endpoint!

## Testing with Postman

### Import Collection

1. Download OpenAPI schema: `http://127.0.0.1:8000/openapi.json`
2. In Postman: **Import** → **OpenAPI** → Select file
3. Collection will be automatically created

### Setup Environment

Create a Postman environment with:

```json
{
  "base_url": "http://127.0.0.1:8000",
  "access_token": ""
}
```

### Auto-Set Token

Add this to login request **Tests** tab:

```javascript
pm.test("Save access token", function () {
    var jsonData = pm.response.json();
    pm.environment.set("access_token", jsonData.access_token);
});
```

### Use Token in Requests

In **Authorization** tab:
- Type: `Bearer Token`
- Token: `{{access_token}}`

## Python Client Example

```python
import requests

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.access_token = None
    
    def login(self, email: str, password: str):
        """Login and store access token."""
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        
        data = response.json()
        self.access_token = data["access_token"]
        return data
    
    def get_headers(self):
        """Get headers with authorization."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def get_current_user(self):
        """Get current user profile."""
        response = requests.get(
            f"{self.base_url}/api/me",
            headers=self.get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def create_user(self, user_data: dict):
        """Create new user (requires permission)."""
        response = requests.post(
            f"{self.base_url}/api/users",
            json=user_data,
            headers=self.get_headers()
        )
        response.raise_for_status()
        return response.json()

# Usage
client = APIClient("http://127.0.0.1:8000")
client.login("admin@example.com", "admin123")

profile = client.get_current_user()
print(f"Logged in as: {profile['email']}")

new_user = client.create_user({
    "email": "newuser@example.com",
    "password": "SecurePass123!",
    "full_name": "New User"
})
print(f"Created user: {new_user['id']}")
```

## JavaScript/TypeScript Client Example

```typescript
// api-client.ts
class APIClient {
  private baseURL: string;
  private accessToken: string | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  async login(email: string, password: string) {
    const response = await fetch(`${this.baseURL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) throw new Error('Login failed');

    const data = await response.json();
    this.accessToken = data.access_token;
    return data;
  }

  private getHeaders() {
    return {
      'Authorization': `Bearer ${this.accessToken}`,
      'Content-Type': 'application/json'
    };
  }

  async getCurrentUser() {
    const response = await fetch(`${this.baseURL}/api/me`, {
      headers: this.getHeaders()
    });

    if (!response.ok) throw new Error('Failed to get user');
    return response.json();
  }

  async createUser(userData: any) {
    const response = await fetch(`${this.baseURL}/api/users`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(userData)
    });

    if (!response.ok) throw new Error('Failed to create user');
    return response.json();
  }
}

// Usage
const client = new APIClient('http://127.0.0.1:8000');

await client.login('admin@example.com', 'admin123');
const profile = await client.getCurrentUser();
console.log(`Logged in as: ${profile.email}`);
```

## WebSocket Support

!!! info "Future Feature"
    WebSocket support for real-time notifications is planned for future versions.

## API Best Practices

### 1. Always Use HTTPS in Production

```python
# .env production
DATABASE_URL=postgresql://user:pass@localhost/db
ALLOWED_ORIGINS=https://your-app.com
```

### 2. Handle Errors Properly

```python
try:
    response = requests.post(url, json=data)
    response.raise_for_status()
except requests.HTTPError as e:
    if e.response.status_code == 401:
        # Re-authenticate
        pass
    elif e.response.status_code == 422:
        # Handle validation error
        errors = e.response.json()['detail']
        pass
```

### 3. Refresh Tokens Before Expiry

```python
import jwt
from datetime import datetime

def is_token_expiring_soon(token: str, threshold: int = 300):
    """Check if token expires in next 5 minutes."""
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        exp = datetime.fromtimestamp(payload['exp'])
        now = datetime.now()
        return (exp - now).total_seconds() < threshold
    except:
        return True

if is_token_expiring_soon(access_token):
    # Refresh token
    new_tokens = client.refresh_token(refresh_token)
    access_token = new_tokens['access_token']
```

### 4. Implement Retry Logic

```python
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(
    total=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504)
)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)
```

## Detailed Endpoint Documentation

Explore detailed documentation for each API category:

- [Authentication](authentication.md) - Registration, login, password management
- [User Management](users.md) - CRUD operations for users
- [Roles & Permissions](roles-permissions.md) - RBAC system
- [OTP Verification](otp.md) - One-time password system

## Need Help?

- [Troubleshooting](../troubleshooting/common-issues.md)
- [FAQ](../troubleshooting/faq.md)
- [GitHub Issues](https://github.com/panjidwisatrio/fastapi-clean-architecture/issues)
