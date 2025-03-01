# FastAPI Clean Architecture

A modern, scalable web application template built with FastAPI following clean architecture principles.

## 📋 Table of Contents
- [Architecture Overview](#architecture-overview)
- [Built-in Features](#built-in-features)
- [Environment Setup](#environment-setup)
- [Production Setup](#production-setup)
- [Getting Started](#getting-started)

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

## 🛠️ Built-in Features

- **Authentication & Authorization**
  - JWT-based authentication
  - Role-based access control
  - Secure password hashing

- **Database Integration**
  - SQLAlchemy ORM support
  - Database migrations with Alembic (on-going)
  - Repository pattern implementation (on-going)

- **API Documentation**
  - Automatic OpenAPI/Swagger documentation
  - API versioning (on-going)

- **Validation**
  - Request validation with Pydantic
  - Custom validation rules (on-going)

- **Testing**
  - Pytest configuration (on-going)
  - Test fixtures (on-going)
  - Mocking utilities (on-going)

- **Logging & Monitoring**
  - Structured logging (on-going)
  - Performance metrics

- **Error Handling**
  - Global exception handling
  - Custom error responses (on-going)

## 🔧 Environment Setup

The application supports multiple environments:

1. Copy `.env.example` to create your environment files:
   ```bash
   # Unix/Linux/macOS
   cp .env.example .env.development
   cp .env.example .env.testing
   cp .env.example .env.production
   
   # Windows
   copy .env.example .env.development
   copy .env.example .env.testing
   copy .env.example .env.production
   ```

2. Customize each file according to environment needs

3. Set the environment variable to specify which configuration to use:

   **Unix/Linux/macOS:**
   ```bash
   # For development
   export ENVIRONMENT=development
   
   # For testing
   export ENVIRONMENT=testing
   
   # For production
   export ENVIRONMENT=production
   ```

   **Windows (Command Prompt):**
   ```cmd
   # For development
   set ENVIRONMENT=development
   
   # For testing
   set ENVIRONMENT=testing
   
   # For production
   set ENVIRONMENT=production
   ```

   **Windows (PowerShell):**
   ```powershell
   # For development
   $env:ENVIRONMENT = "development"
   
   # For testing
   $env:ENVIRONMENT = "testing"
   
   # For production
   $env:ENVIRONMENT = "production"
   ```

4. If no ENVIRONMENT variable is set, the application defaults to the development environment

## 🚀 Production Setup

In production, sensitive values use environment variable substitution. For example, `${PROD_SECRET_KEY}` in .env.production will be replaced with the actual value of the PROD_SECRET_KEY environment variable.

### Setting up production environment variables:

**Unix/Linux/macOS:**
```bash
# Set these on your production server
export PROD_SECRET_KEY=your_secure_production_key
export PROD_DATABASE_URL=your_production_database_connection_string

# Then run the application with:
export ENVIRONMENT=production
python -m app.main
```

This approach keeps sensitive production credentials out of configuration files and version control.

## 📄 License

This project is licensed under the MIT License.
