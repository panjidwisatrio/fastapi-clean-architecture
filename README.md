# FastAPI Clean Architecture

A modern, production-ready web application template built with FastAPI following clean architecture principles. This template provides a robust foundation for building scalable REST APIs with authentication, authorization, and comprehensive feature set.

## 📋 Table of Contents
- [Features](#-features)
- [Architecture Overview](#-architecture-overview)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Data Configuration](#-data-configuration)
- [Environment Setup](#-environment-setup)
- [Running the Application](#-running-the-application)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Production Deployment](#-production-deployment)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### Core Features
- **🔐 Authentication & Authorization**
  - JWT-based authentication with access tokens
  - Secure password hashing using bcrypt
  - Role-based access control (RBAC)
  - Permission-based authorization
  - Token blacklist for logout functionality
  
- **👤 User Management**
  - User registration and login
  - Profile management
  - Password reset with email verification
  - Email domain validation
  - User roles and permissions

- **📧 Email Services**
  - SMTP email integration (Gmail support)
  - Async email sending
  - Password reset emails
  - OTP verification emails

- **🔑 OTP System**
  - One-Time Password generation
  - Configurable OTP length and expiration
  - Email-based OTP delivery
  - Secure OTP validation

- **📝 API Features**
  - RESTful API design
  - Automatic OpenAPI/Swagger documentation
  - Request/response validation with Pydantic
  - Comprehensive error handling
  - CORS support

- **🗄️ Database**
  - SQLAlchemy ORM integration
  - PostgreSQL/MySQL/SQLite support
  - Database initialization with seed data
  - Repository pattern implementation

- **📊 Logging & Monitoring**
  - Structured logging
  - Request/response logging
  - Environment-based log configuration
  - Rotating file handler support

## 🏛️ Architecture Overview

This project implements Clean Architecture principles, separating concerns into distinct layers:

### Layers
1. **Domain Layer** - Contains enterprise business rules and entities
   - Database models (e.g., `app/models/user.py`)
   ```python
   class User(Base):
       __tablename__ = "users"
       id = Column(Integer, primary_key=True, index=True)
       role_id = Column(Integer, ForeignKey("roles.id"))
       # More fields...
   ```

2. **Use Case Layer** - Contains application-specific business rules
   - Services (e.g., `app/services/user_service.py`)
   ```python
   class UserService:
       def __init__(self, user_repository: UserRepository):
           self.user_repository = user_repository
   
       def authenticate_user(self, email: str, password: str) -> User:
           # Business logic implementation
   ```
   - DTOs (`app/schemas/user.py`)
   ```python
   class UserCreate(UserBase):
       password: str
       roles_id: Optional[int] = None
   ```

3. **Interface Adapters Layer** - Contains adapters between use cases and frameworks
   - API Routes (`app/api/routes/user.py`)
   ```python
   @router.post("/register", response_model=User)
   def register_user(user: UserRegister, service: UserService = Depends(get_user_service)):
       return service.create_user(user)
   ```
   - Repositories (`app/repositories/user_repository.py`)
   ```python
   class UserRepository:
       def __init__(self, db: Session):
           self.db = db
       
       def get_user_by_email(self, email: str) -> User:
           return self.db.query(User).filter(User.email == email).first()
   ```

4. **Frameworks & Drivers Layer** - Contains external frameworks and tools
   - Dependency injection (`app/api/dependencies.py`)
   ```python
   def get_user_service(db: Session = Depends(get_db)) -> UserService:
       return UserService(UserRepository(db))
   ```
   - Database configuration
   - FastAPI framework

### Data Flow
1. HTTP request arrives at a router endpoint (`app/api/routes/user.py`)
2. Router gets the appropriate service via dependency injection
3. Service contains business logic and calls repository methods
4. Repository interacts with database models
5. Data flows back through the layers, transformed by schemas

### Benefits
- **Independence of frameworks**: The business logic doesn't depend on FastAPI or any database
- **Testability**: Business rules can be tested without UI, database, or any external element
- **Independence of UI**: The UI can change without changing the rest of the system
- **Independence of Database**: Business rules aren't bound to a specific database

## 📁 Project Structure

```
fastapi-clean-architecture/
├── app/
│   ├── api/                    # API layer
│   │   ├── dependencies.py     # Dependency injection
│   │   └── routes/             # API endpoints
│   │       ├── auth.py         # Authentication routes
│   │       ├── user.py         # User management routes
│   │       ├── role.py         # Role management routes
│   │       ├── permission.py   # Permission routes
│   │       ├── otp.py          # OTP routes
│   │       └── me.py           # Current user routes
│   │
│   ├── core/                   # Core application configuration
│   │   ├── config.py           # Application settings
│   │   ├── database.py         # Database configuration
│   │   ├── security.py         # Security utilities
│   │   ├── logging.py          # Logging configuration
│   │   ├── init_db.py          # Database initialization
│   │   └── utils.py            # Utility functions
│   │
│   ├── models/                 # Database models (Domain layer)
│   │   ├── user.py
│   │   ├── role.py
│   │   ├── permission.py
│   │   ├── permission_role.py
│   │   ├── otp.py
│   │   └── token_blacklist.py
│   │
│   ├── repositories/           # Data access layer
│   │   ├── user_repository.py
│   │   ├── role_repository.py
│   │   ├── permission_repository.py
│   │   ├── otp_repository.py
│   │   └── token_blacklist_repository.py
│   │
│   ├── schemas/                # Pydantic schemas (DTOs)
│   │   ├── user.py
│   │   ├── role.py
│   │   ├── permission.py
│   │   ├── auth.py
│   │   ├── token.py
│   │   └── otp.py
│   │
│   ├── services/               # Business logic layer
│   │   ├── user_service.py
│   │   ├── auth_service.py
│   │   ├── role_service.py
│   │   ├── permission_service.py
│   │   ├── otp_service.py
│   │   ├── email_service.py
│   │   └── token_blacklist_service.py
│   │
│   ├── data/                   # Initial data for seeding
│   │   ├── initial_data.json
│   │   └── permissions.json
│   │
│   ├── tests/                  # Test files
│   │   └── test_env.py
│   │
│   └── main.py                 # Application entry point
│
├── logs/                       # Application logs
├── .env.example                # Environment variables template
├── requirements.txt            # Python dependencies
├── LICENSE                     # MIT License
└── README.md                   # This file
```

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **pip** - Python package installer (usually comes with Python)
- **PostgreSQL/MySQL/SQLite** - Database (SQLite works out of the box for development)
- **Git** - Version control system

Optional but recommended:
- **Virtual Environment** - `venv` or `virtualenv` for isolated Python environments
- **Postman** or **Thunder Client** - For API testing

## 🚀 Installation

### Quick Start Guide

Follow these steps to get the application running:

1. **Clone and Setup**
   ```bash
   git clone https://github.com/yourusername/fastapi-clean-architecture.git
   cd fastapi-clean-architecture
   ```

2. **Create Virtual Environment**
   
   Windows (PowerShell):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
   
   Unix/Linux/macOS:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare Data Files** (⚠️ Important!)
   - Ensure `app/data/initial_data.json` exists with super admin credentials
   - Ensure `app/data/permissions.json` exists with roles and permissions
   - See [Data Configuration](#-data-configuration) section for details

5. **Configure Environment**
   - Copy `.env.example` to `.env.development`
   - Update the environment variables (especially `SECRET_KEY` and `DATABASE_URL`)
   - See [Environment Setup](#-environment-setup) section for details

6. **Run the Application**
   ```bash
   uvicorn app.main:app --reload
   ```

7. **Access the Application**
   - API: `http://localhost:8000`
   - Swagger Docs: `http://localhost:8000/docs`
   - Login with super admin credentials from `initial_data.json`

### Detailed Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/fastapi-clean-architecture.git
cd fastapi-clean-architecture
```

### 2. Create Virtual Environment

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Unix/Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 🗃️ Data Configuration

Before running the application, you need to prepare the initial data files in the `app/data/` directory. These files are used to seed the database with initial roles, permissions, and admin user.

### 1. Create `initial_data.json`

Create or edit `app/data/initial_data.json` to define the super admin user:

**File:** `app/data/initial_data.json`

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

**JSON Schema:**

```json
{
  "super_admin": {
    "first_name": "string",      // First name of the super admin
    "last_name": "string",        // Last name of the super admin
    "email": "string (email)",    // Email address (must be valid email format)
    "password": "string"          // Password (will be hashed automatically)
  }
}
```

**Notes:**
- The `email` will be used for login
- The `password` should be strong and will be hashed before storing
- This user will have all permissions defined in `permissions.json`
- Change these default credentials before deploying to production!

### 2. Create `permissions.json`

Create or edit `app/data/permissions.json` to define roles and permissions:

**File:** `app/data/permissions.json`

```json
{
  "scopes": {
    "create_user": "Create new user",
    "get_all_users_info": "Read all users information",
    "get_user_info_by_id": "Read user information by id",
    "update_user_info": "Update user information",
    "update_user_role": "Update user role",
    "update_user_active_status": "Update user active status",
    "get_all_roles": "Read all roles",
    "get_all_scopes": "Read all scopes",
    "get_scope_by_role": "Read scope by role",
    "get_profile_info": "Read profile information",
    "update_profile_info": "Update profile information",
    "update_profile_password": "Update password",
    "delete_profile": "Delete profile"
  },
  "roles": {
    "Super Admin": {
      "description": "Super Admin has all permissions",
      "permissions": [
        "create_user",
        "get_all_users_info",
        "get_user_info_by_id",
        "update_user_info",
        "update_user_role",
        "update_user_active_status",
        "get_all_roles",
        "get_all_scopes",
        "get_scope_by_role",
        "get_profile_info",
        "update_profile_info",
        "update_profile_password",
        "delete_profile"
      ]
    },
    "Admin": {
      "description": "Admin can manage users and view data",
      "permissions": [
        "get_all_users_info",
        "get_user_info_by_id",
        "update_user_info",
        "get_all_roles",
        "get_profile_info",
        "update_profile_info",
        "update_profile_password"
      ]
    },
    "User": {
      "description": "Regular user with basic permissions",
      "permissions": [
        "get_profile_info",
        "update_profile_info",
        "update_profile_password"
      ]
    }
  }
}
```

**JSON Schema:**

```json
{
  "scopes": {
    "permission_name": "string (description)"
    // Add more permissions as needed
    // Format: "permission_key": "Human readable description"
  },
  "roles": {
    "Role Name": {
      "description": "string",           // Description of the role
      "permissions": [
        "string"                          // Array of permission keys from "scopes"
      ]
    }
    // Add more roles as needed
  }
}
```

**Schema Explanation:**

1. **`scopes` object**: Defines all available permissions in the system
   - Key: Permission identifier (snake_case format)
   - Value: Human-readable description of the permission

2. **`roles` object**: Defines user roles and their associated permissions
   - Key: Role name (string with spaces allowed)
   - Value: Object containing:
     - `description`: Explanation of what the role can do
     - `permissions`: Array of permission keys from the `scopes` object

**Example: Adding Custom Permissions**

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

### 3. Verify Data Files

Before running the application, ensure:

- [ ] `app/data/initial_data.json` exists and contains valid super admin data
- [ ] `app/data/permissions.json` exists and contains at least one role
- [ ] All permission keys in `roles.permissions` arrays exist in the `scopes` object
- [ ] Email in `initial_data.json` is valid format
- [ ] Password is strong enough for your security requirements

### 4. Database Initialization

When you start the application for the first time, it will automatically:

1. Create all database tables
2. Load permissions from `permissions.json`
3. Create roles with their associated permissions
4. Create the super admin user from `initial_data.json`

**Check the logs on startup:**

```
INFO:app:Application starting in development environment
INFO:app:Initializing database on startup
INFO:app:Created permission: create_user
INFO:app:Created role: Super Admin
INFO:app:Added permission create_user to role Super Admin
INFO:app:Created super admin user: admin@example.com
INFO:app:Database initialization completed
```

### 5. Validate JSON Files (Optional)

You can validate your JSON files before starting the application:

**Using Python:**

```python
# validate_data.py
import json
import sys

def validate_json_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✓ {filepath} is valid JSON")
        return True
    except FileNotFoundError:
        print(f"✗ {filepath} not found!")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ {filepath} has JSON syntax error: {e}")
        return False

def validate_permissions_structure(data):
    """Validate permissions.json structure"""
    if "scopes" not in data:
        print("✗ Missing 'scopes' key in permissions.json")
        return False
    if "roles" not in data:
        print("✗ Missing 'roles' key in permissions.json")
        return False
    
    # Check all role permissions exist in scopes
    scopes = data["scopes"]
    for role_name, role_data in data["roles"].items():
        if "permissions" not in role_data:
            print(f"✗ Role '{role_name}' missing 'permissions' array")
            return False
        for perm in role_data["permissions"]:
            if perm not in scopes:
                print(f"✗ Permission '{perm}' in role '{role_name}' not found in scopes")
                return False
    
    print("✓ permissions.json structure is valid")
    return True

def validate_initial_data_structure(data):
    """Validate initial_data.json structure"""
    if "super_admin" not in data:
        print("✗ Missing 'super_admin' key in initial_data.json")
        return False
    
    required_fields = ["first_name", "last_name", "email", "password"]
    super_admin = data["super_admin"]
    
    for field in required_fields:
        if field not in super_admin:
            print(f"✗ Missing '{field}' in super_admin")
            return False
    
    # Basic email validation
    if "@" not in super_admin["email"]:
        print(f"✗ Invalid email format: {super_admin['email']}")
        return False
    
    print("✓ initial_data.json structure is valid")
    return True

if __name__ == "__main__":
    print("Validating data files...\n")
    
    # Validate initial_data.json
    initial_data_valid = validate_json_file("app/data/initial_data.json")
    if initial_data_valid:
        with open("app/data/initial_data.json", 'r') as f:
            initial_data = json.load(f)
        validate_initial_data_structure(initial_data)
    
    print()
    
    # Validate permissions.json
    permissions_valid = validate_json_file("app/data/permissions.json")
    if permissions_valid:
        with open("app/data/permissions.json", 'r') as f:
            permissions_data = json.load(f)
        validate_permissions_structure(permissions_data)
    
    print("\n" + "="*50)
    if initial_data_valid and permissions_valid:
        print("✓ All data files are valid!")
        sys.exit(0)
    else:
        print("✗ Some data files have errors. Please fix them before running the app.")
        sys.exit(1)
```

**Run validation:**

```bash
python validate_data.py
```

**Expected output:**

```
Validating data files...

✓ app/data/initial_data.json is valid JSON
✓ initial_data.json structure is valid

✓ app/data/permissions.json is valid JSON
✓ permissions.json structure is valid

==================================================
✓ All data files are valid!
```

### 6. Tips for Data Files

**Security Best Practices:**

- ✅ **Change default credentials**: Never use default passwords in production
- ✅ **Use strong passwords**: Minimum 12 characters with mixed case, numbers, and symbols
- ✅ **Rotate secrets regularly**: Update passwords and keys periodically
- ✅ **Restrict permissions**: Give users only the permissions they need
- ✅ **Version control**: Don't commit actual credentials to Git (use `.env` files)

**Customization Tips:**

1. **Adding New Permissions:**
   - Add to `scopes` first
   - Then add to appropriate roles' `permissions` array
   - Implement the permission check in your route decorators

2. **Creating New Roles:**
   - Add role definition in `permissions.json`
   - Assign relevant permissions from existing scopes
   - Consider role hierarchy (User → Admin → Super Admin)

3. **Multiple Admin Users:**
   - You can only define one super admin in `initial_data.json`
   - Create additional admins through the API after first startup
   - Or modify `init_db.py` to support multiple initial users

4. **Email Domain Restrictions:**
   - Set `ACCEPTED_EMAIL_DOMAINS` in environment variables
   - Use comma-separated list: `example.com,company.com`
   - Leave empty or use `*` to accept all domains (not recommended)

## 🛠️ Environment Setup

### Environment Configuration

The application supports multiple environments (development, testing, production). Each environment can have its own configuration file.

### 1. Create Environment Files

Copy the example environment file to create your environment-specific configurations:

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env.development
Copy-Item .env.example .env.testing
Copy-Item .env.example .env.production
```

**Unix/Linux/macOS:**
```bash
cp .env.example .env.development
cp .env.example .env.testing
cp .env.example .env.production
```

### 2. Configure Environment Variables

Edit each `.env.*` file with your specific configuration. Here are the key variables:

```bash
# Environment
ENVIRONMENT=development  # development, testing, or production

# App URL (for email links)
APP_URL=http://localhost:8000
RESET_PASSWORD_ENDPOINT=/users/reset-password

# Security - Generate with: openssl rand -hex 32
SECRET_KEY=your_super_secret_key_here_change_this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Domain Validation (comma-separated)
ACCEPTED_EMAIL_DOMAINS=example.com,yourdomain.com

# Database
DATABASE_URL=sqlite:///./test.db
# For PostgreSQL: postgresql://user:password@localhost/dbname
# For MySQL: mysql://user:password@localhost/dbname

# Gmail SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Use App Password if 2FA enabled
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=Your App Name

# OTP Configuration
OTP_EXPIRE_MINUTES=5
OTP_LENGTH=6
```

### 3. Set Active Environment

Set the `ENVIRONMENT` variable to specify which configuration to use:

**Windows (PowerShell):**
```powershell
$env:ENVIRONMENT = "development"  # or "testing", "production"
```

**Windows (Command Prompt):**
```cmd
set ENVIRONMENT=development
```

**Unix/Linux/macOS:**
```bash
export ENVIRONMENT=development
```

> **Note:** If no `ENVIRONMENT` variable is set, the application defaults to `development`.

### 4. Gmail SMTP Setup (Optional but Recommended)

To enable email functionality:

1. Go to your Google Account settings
2. Enable 2-Factor Authentication
3. Generate an App Password: [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
4. Use the generated password in `SMTP_PASSWORD`

## 🏃 Running the Application

### Development Mode

Start the development server with auto-reload:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or using Python module:

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at:
- **API Base URL**: `http://localhost:8000`
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Production Mode

For production, run without reload and with appropriate workers:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Or use Gunicorn with Uvicorn workers:

```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📚 API Documentation

Once the application is running, you can access the interactive API documentation:

### Swagger UI (Recommended)
Navigate to `http://localhost:8000/docs` for an interactive API documentation where you can:
- View all available endpoints
- Test API endpoints directly from the browser
- See request/response schemas
- Authenticate and test protected endpoints

### ReDoc
Navigate to `http://localhost:8000/redoc` for an alternative, clean API documentation view.

### Available Endpoints

**Authentication:**
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get access token
- `POST /auth/logout` - Logout and blacklist token
- `POST /auth/refresh` - Refresh access token
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password with token

**User Management:**
- `GET /users` - List all users (Admin only)
- `GET /users/{id}` - Get user by ID
- `POST /users` - Create new user (Admin only)
- `PUT /users/{id}` - Update user (Admin only)
- `DELETE /users/{id}` - Delete user (Admin only)

**Current User:**
- `GET /me` - Get current user profile
- `PUT /me` - Update current user profile
- `PUT /me/password` - Change password

**Roles & Permissions:**
- `GET /roles` - List all roles
- `GET /permissions` - List all permissions
- `POST /roles` - Create new role (Admin only)
- `PUT /roles/{id}` - Update role (Admin only)

**OTP:**
- `POST /otp/send` - Send OTP to email
- `POST /otp/verify` - Verify OTP code

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest app/tests/test_env.py

# Run with verbose output
pytest -v
```

### Test Environment

Tests use the `.env.testing` configuration. Make sure to create and configure it before running tests.

## ⚠️ Troubleshooting

### Common Issues and Solutions

#### 1. Database Initialization Errors

**Problem:** `FileNotFoundError: [Errno 2] No such file or directory: 'app/data/initial_data.json'`

**Solution:**
- Ensure `app/data/initial_data.json` exists
- Check the file path is correct
- Verify the file contains valid JSON
- See [Data Configuration](#-data-configuration) section

#### 2. Permission Loading Errors

**Problem:** `KeyError` or permission not found errors during startup

**Solution:**
- Verify `app/data/permissions.json` exists and is valid JSON
- Ensure all permission keys in `roles.permissions` exist in `scopes`
- Check for typos in permission names
- Validate JSON syntax using a JSON validator

#### 3. Super Admin Login Fails

**Problem:** Cannot login with credentials from `initial_data.json`

**Solution:**
- Check database was initialized correctly (check logs)
- Verify email domain is in `ACCEPTED_EMAIL_DOMAINS` environment variable
- Try deleting the database file and restarting (development only)
- Check password is correct (case-sensitive)

#### 4. Email Sending Fails

**Problem:** OTP or password reset emails not sending

**Solution:**
- Verify SMTP credentials in environment file
- For Gmail, use App Password instead of regular password
- Check `SMTP_USER` and `SMTP_FROM_EMAIL` are correct
- Ensure 2FA is enabled and App Password is generated

#### 5. JWT Token Errors

**Problem:** `Invalid token` or authentication errors

**Solution:**
- Ensure `SECRET_KEY` is set and not empty
- Generate new secret key: `openssl rand -hex 32`
- Check token hasn't expired (`ACCESS_TOKEN_EXPIRE_MINUTES`)
- Clear browser cookies/local storage and login again

#### 6. Database Connection Errors

**Problem:** `could not connect to server` or database errors

**Solution:**
- Check `DATABASE_URL` format is correct
- For SQLite: `sqlite:///./test.db`
- For PostgreSQL: `postgresql://user:password@localhost/dbname`
- For MySQL: `mysql://user:password@localhost/dbname`
- Ensure database server is running (PostgreSQL/MySQL)

#### 7. Module Import Errors

**Problem:** `ModuleNotFoundError` when starting application

**Solution:**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version is 3.8 or higher
- Try: `pip install --upgrade pip`

#### 8. Permission Denied Errors

**Problem:** Cannot create log files or database files

**Solution:**
- Check write permissions in `logs/` directory
- Run with appropriate user permissions
- Create directories manually: `mkdir logs`

### Getting Help

If you encounter issues not listed here:

1. Check the application logs in `logs/` directory
2. Review the startup logs in the terminal
3. Verify all environment variables are set correctly
4. Check the [GitHub Issues](https://github.com/yourusername/fastapi-clean-architecture/issues)
5. Create a new issue with:
   - Error message and stack trace
   - Steps to reproduce
   - Environment details (OS, Python version)
   - Configuration (without sensitive data)

## 🚀 Production Deployment

### Environment Variables for Production

In production, use environment variable substitution for sensitive values. For example, `${PROD_SECRET_KEY}` in `.env.production` will be replaced with the actual value of the `PROD_SECRET_KEY` environment variable.

**Set production environment variables:**

```bash
export PROD_SECRET_KEY=your_secure_production_key
export PROD_DATABASE_URL=postgresql://user:pass@host/db
export PROD_SMTP_PASSWORD=your_smtp_app_password
export ENVIRONMENT=production
```

### Deployment Options

#### 1. Docker Deployment (Recommended)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t fastapi-app .
docker run -p 8000:8000 --env-file .env.production fastapi-app
```

#### 2. Cloud Platforms

- **AWS**: Deploy to EC2, ECS, or Lambda
- **Google Cloud**: Deploy to Cloud Run or App Engine
- **Azure**: Deploy to App Service
- **Heroku**: Use Procfile for deployment
- **DigitalOcean**: Deploy to App Platform or Droplets

### Production Checklist

- [ ] Set strong `SECRET_KEY`
- [ ] Configure production database
- [ ] Set up HTTPS/SSL
- [ ] Configure CORS for your frontend domain
- [ ] Set up proper logging and monitoring
- [ ] Enable rate limiting
- [ ] Set up database backups
- [ ] Configure environment variables securely
- [ ] Review and restrict `ACCEPTED_EMAIL_DOMAINS`
- [ ] Set up firewall rules
- [ ] Enable database migrations
- [ ] Configure CDN for static files (if any)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Write meaningful commit messages
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework for building APIs
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and ORM
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation using Python type hints
- [Uvicorn](https://www.uvicorn.org/) - Lightning-fast ASGI server

## 📞 Support

If you have any questions or need help, please:

- Open an issue on GitHub
- Check the [documentation](http://localhost:8000/docs) when running the app
- Review the code examples in the repository

## 🗺️ Roadmap

- [ ] Add database migrations with Alembic
- [ ] Implement API versioning
- [ ] Add comprehensive test suite
- [ ] Add rate limiting
- [ ] Add caching layer (Redis)
- [ ] Add WebSocket support
- [ ] Add file upload functionality
- [ ] Add background tasks with Celery
- [ ] Add GraphQL support
- [ ] Add Docker Compose setup
- [ ] Add CI/CD pipeline examples

---

**Made with ❤️ using FastAPI and Clean Architecture principles**