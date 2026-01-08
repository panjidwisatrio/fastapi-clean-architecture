# User Management API

API endpoints for managing users in the system.

## Overview

The User Management API provides CRUD (Create, Read, Update, Delete) operations for user accounts. All endpoints require authentication and appropriate permissions.

## Permissions Required

| Operation | Permission | Description |
|-----------|------------|-------------|
| List users | `user:read` | View all users |
| Get user | `user:read` | View specific user |
| Create user | `user:create` | Create new user |
| Update user | `user:update` | Update user information |
| Delete user | `user:delete` | Delete user account |

## Endpoints

### List All Users

Get paginated list of all users.

```http
GET /users/?skip=0&limit=10
```

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Query Parameters:**

- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum records to return (default: 100, max: 100)

**Response** (200 OK):

```json
[
  {
    "id": 1,
    "email": "user1@example.com",
    "full_name": "User One",
    "is_active": true,
    "is_verified": true,
    "role_id": 2,
    "created_at": "2024-01-15T10:30:00Z"
  },
  {
    "id": 2,
    "email": "user2@example.com",
    "full_name": "User Two",
    "is_active": true,
    "is_verified": false,
    "role_id": 2,
    "created_at": "2024-01-16T11:20:00Z"
  }
]
```

**Example:**

```bash
curl -X GET "http://127.0.0.1:8000/users/?skip=0&limit=10" \
  -H "Authorization: Bearer eyJhbGc..."
```

### Get User by ID

Get details of a specific user.

```http
GET /users/{user_id}
```

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Path Parameters:**

- `user_id` (int, required): User ID

**Response** (200 OK):

```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": true,
  "role_id": 2,
  "role": {
    "id": 2,
    "name": "User",
    "description": "Regular user"
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**

- `404 Not Found`: User not found
- `403 Forbidden`: Insufficient permissions

**Example:**

```bash
curl -X GET "http://127.0.0.1:8000/users/1" \
  -H "Authorization: Bearer eyJhbGc..."
```

### Create New User

Create a new user account (admin only).

```http
POST /users/
```

**Headers:**
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "email": "newuser@example.com",
  "password": "SecurePass123!",
  "full_name": "New User",
  "role_id": 2,
  "is_active": true
}
```

**Response** (201 Created):

```json
{
  "id": 42,
  "email": "newuser@example.com",
  "full_name": "New User",
  "is_active": true,
  "is_verified": false,
  "role_id": 2,
  "created_at": "2024-01-20T14:30:00Z"
}
```

**Error Responses:**

- `400 Bad Request`: Email already exists
- `403 Forbidden`: Insufficient permissions
- `422 Unprocessable Entity`: Validation error

**Example:**

```bash
curl -X POST "http://127.0.0.1:8000/users/" \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123!",
    "full_name": "New User",
    "role_id": 2
  }'
```

### Update User

Update user information.

```http
PUT /users/{user_id}
```

**Headers:**
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Path Parameters:**

- `user_id` (int, required): User ID

**Request Body:**

```json
{
  "email": "updated@example.com",
  "full_name": "Updated Name",
  "is_active": true,
  "role_id": 3
}
```

!!! note "Partial Updates"
    All fields are optional. Only provided fields will be updated.

**Response** (200 OK):

```json
{
  "id": 42,
  "email": "updated@example.com",
  "full_name": "Updated Name",
  "is_active": true,
  "is_verified": false,
  "role_id": 3,
  "created_at": "2024-01-20T14:30:00Z"
}
```

**Error Responses:**

- `404 Not Found`: User not found
- `400 Bad Request`: Email already in use
- `403 Forbidden`: Insufficient permissions

**Example:**

```bash
curl -X PUT "http://127.0.0.1:8000/users/42" \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Updated Name",
    "is_active": true
  }'
```

### Delete User

Delete a user account.

```http
DELETE /users/{user_id}
```

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Path Parameters:**

- `user_id` (int, required): User ID

**Response** (204 No Content):

No response body.

**Error Responses:**

- `404 Not Found`: User not found
- `403 Forbidden`: Insufficient permissions

**Example:**

```bash
curl -X DELETE "http://127.0.0.1:8000/users/42" \
  -H "Authorization: Bearer eyJhbGc..."
```

## Current User Endpoints

Special endpoints for authenticated users to manage their own profile.

### Get Current User Profile

Get profile of the currently authenticated user.

```http
GET /me/
```

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response** (200 OK):

```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": true,
  "role_id": 2,
  "role": {
    "id": 2,
    "name": "User",
    "description": "Regular user",
    "permissions": [
      {
        "id": 1,
        "name": "read:own_profile",
        "description": "Read own profile"
      }
    ]
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Example:**

```bash
curl -X GET "http://127.0.0.1:8000/me/" \
  -H "Authorization: Bearer eyJhbGc..."
```

### Update Current User Profile

Update your own profile information.

```http
PUT /me/
```

**Headers:**
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "full_name": "John Updated Doe",
  "email": "john.new@example.com"
}
```

!!! info "Restrictions"
    Users cannot change their own:
    - Role
    - Active status
    - Verified status

**Response** (200 OK):

```json
{
  "id": 1,
  "email": "john.new@example.com",
  "full_name": "John Updated Doe",
  "is_active": true,
  "is_verified": true,
  "role_id": 2,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Example:**

```bash
curl -X PUT "http://127.0.0.1:8000/me/" \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Updated Doe"
  }'
```

### Delete Current User Account

Delete your own account (soft delete).

```http
DELETE /me/
```

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Response** (204 No Content):

No response body.

!!! warning "Account Deletion"
    This marks the account as inactive. Data may be retained for legal/compliance reasons.

**Example:**

```bash
curl -X DELETE "http://127.0.0.1:8000/me/" \
  -H "Authorization: Bearer eyJhbGc..."
```

## User Schema

### User Object

```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "role_id": 2,
  "role": {
    "id": 2,
    "name": "User"
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Fields:**

- `id` (integer): Unique user identifier
- `email` (string): User email address (unique)
- `full_name` (string): User's full name
- `is_active` (boolean): Account active status
- `is_verified` (boolean): Email verified status
- `role_id` (integer): Associated role ID
- `role` (object): Role details with permissions
- `created_at` (datetime): Account creation timestamp

## Code Examples

### Python Client

```python
import requests

class UserClient:
    def __init__(self, base_url: str, access_token: str):
        self.base_url = base_url
        self.access_token = access_token
    
    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def list_users(self, skip: int = 0, limit: int = 10):
        response = requests.get(
            f"{self.base_url}/api/users",
            params={"skip": skip, "limit": limit},
            headers=self.get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_user(self, user_id: int):
        response = requests.get(
            f"{self.base_url}/api/users/{user_id}",
            headers=self.get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def create_user(self, email: str, password: str, full_name: str, role_id: int = 2):
        response = requests.post(
            f"{self.base_url}/api/users",
            json={
                "email": email,
                "password": password,
                "full_name": full_name,
                "role_id": role_id
            },
            headers=self.get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def update_user(self, user_id: int, **kwargs):
        response = requests.put(
            f"{self.base_url}/api/users/{user_id}",
            json=kwargs,
            headers=self.get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def delete_user(self, user_id: int):
        response = requests.delete(
            f"{self.base_url}/api/users/{user_id}",
            headers=self.get_headers()
        )
        response.raise_for_status()
        return True

# Usage
client = UserClient("http://127.0.0.1:8000", "your_access_token")

# List users
users = client.list_users(skip=0, limit=10)
print(f"Found {len(users)} users")

# Create user
new_user = client.create_user(
    email="newuser@example.com",
    password="SecurePass123!",
    full_name="New User"
)
print(f"Created user: {new_user['id']}")

# Update user
updated = client.update_user(new_user['id'], full_name="Updated Name")
print(f"Updated: {updated['full_name']}")

# Delete user
client.delete_user(new_user['id'])
print("User deleted")
```

### JavaScript Client

```javascript
class UserClient {
  constructor(baseURL, accessToken) {
    this.baseURL = baseURL;
    this.accessToken = accessToken;
  }

  getHeaders() {
    return {
      'Authorization': `Bearer ${this.accessToken}`,
      'Content-Type': 'application/json'
    };
  }

  async listUsers(skip = 0, limit = 10) {
    const response = await fetch(
      `${this.baseURL}/api/users?skip=${skip}&limit=${limit}`,
      { headers: this.getHeaders() }
    );
    if (!response.ok) throw new Error('Failed to list users');
    return response.json();
  }

  async getUser(userId) {
    const response = await fetch(
      `${this.baseURL}/api/users/${userId}`,
      { headers: this.getHeaders() }
    );
    if (!response.ok) throw new Error('User not found');
    return response.json();
  }

  async createUser(email, password, fullName, roleId = 2) {
    const response = await fetch(`${this.baseURL}/api/users`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ email, password, full_name: fullName, role_id: roleId })
    });
    if (!response.ok) throw new Error('Failed to create user');
    return response.json();
  }

  async updateUser(userId, updates) {
    const response = await fetch(`${this.baseURL}/api/users/${userId}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(updates)
    });
    if (!response.ok) throw new Error('Failed to update user');
    return response.json();
  }

  async deleteUser(userId) {
    const response = await fetch(`${this.baseURL}/api/users/${userId}`, {
      method: 'DELETE',
      headers: this.getHeaders()
    });
    if (!response.ok) throw new Error('Failed to delete user');
    return true;
  }
}

// Usage
const client = new UserClient('http://127.0.0.1:8000', 'your_access_token');

// List users
const users = await client.listUsers(0, 10);
console.log(`Found ${users.length} users`);

// Create user
const newUser = await client.createUser(
  'newuser@example.com',
  'SecurePass123!',
  'New User'
);
console.log(`Created user: ${newUser.id}`);
```

## Best Practices

### 1. Validate Before Create/Update

```python
from pydantic import EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=100)
```

### 2. Handle Errors Gracefully

```python
try:
    user = client.create_user(email, password, full_name)
except requests.HTTPError as e:
    if e.response.status_code == 400:
        print("Email already exists")
    elif e.response.status_code == 403:
        print("Insufficient permissions")
    else:
        print(f"Error: {e.response.json()['detail']}")
```

### 3. Pagination for Large Lists

```python
def get_all_users(client):
    all_users = []
    skip = 0
    limit = 100
    
    while True:
        users = client.list_users(skip=skip, limit=limit)
        if not users:
            break
        all_users.extend(users)
        skip += limit
    
    return all_users
```

## Next Steps

- [Authentication API](authentication.md)
- [Roles & Permissions API](roles-permissions.md)
- [API Overview](overview.md)
