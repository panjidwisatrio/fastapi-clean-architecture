# Data Flow

Understanding how data flows through the application layers.

## Request-Response Cycle

Every API request follows a specific path through the architecture layers. Understanding this flow is crucial for debugging and extending the application.

## Complete Flow Diagram

```mermaid
flowchart TD
    Client["🌐 CLIENT<br/>Browser/Mobile App"]
    
    subgraph Framework1["Framework & Drivers Layer"]
        FastAPI["FastAPI Application<br/>• Receives HTTP request<br/>• Validates format<br/>• Routes to handler"]
    end
    
    subgraph Adapter1["Interface Adapter Layer"]
        Route["API Route Handler<br/>@router.post('/users')<br/>• Typed request (UserCreate)<br/>• Delegates to service"]
    end
    
    subgraph DI["Dependency Injection"]
        Deps["get_user_service()<br/>• Creates UserService<br/>• Injects Repository"]
    end
    
    subgraph UseCase["Use Case Layer"]
        Service["UserService<br/>• Validate email exists<br/>• Hash password<br/>• Business rules"]
    end
    
    subgraph Adapter2["Interface Adapter Layer"]
        Repo["UserRepository<br/>• create(user_data)<br/>• Database abstraction"]
    end
    
    subgraph Domain["Domain Layer"]
        Model["User Model<br/>• Entity definition<br/>• Schema structure"]
    end
    
    subgraph Framework2["Framework & Drivers Layer"]
        DB["Database<br/>PostgreSQL + SQLAlchemy<br/>• INSERT INTO users"]
    end
    
    Response["✅ HTTP 201 Created<br/>{id, email, is_active}"]
    
    Client -->|"POST /api/users"| FastAPI
    FastAPI --> Route
    Route --> Deps
    Deps --> Service
    Service --> Repo
    Repo --> Model
    Model --> DB
    
    DB -.->|"Data"| Model
    Model -.-> Repo
    Repo -.-> Service
    Service -.-> Deps
    Deps -.-> Route
    Route -.-> FastAPI
    FastAPI -.-> Response
    
    style Client fill:#e1f5ff,stroke:#01579b
    style Response fill:#c8e6c9,stroke:#2e7d32
    style Framework1 fill:#e3f2fd,stroke:#1976d2
    style Framework2 fill:#e3f2fd,stroke:#1976d2
    style Adapter1 fill:#e8f5e9,stroke:#388e3c
    style Adapter2 fill:#e8f5e9,stroke:#388e3c
    style UseCase fill:#fff3e0,stroke:#f57c00
    style Domain fill:#ffebee,stroke:#d32f2f
    style DI fill:#f5f5f5,stroke:#616161
```

## Detailed Examples

### Example 1: User Registration

Let's trace a complete user registration request:

#### 1. Client Request

```http
POST /api/users HTTP/1.1
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

#### 2. Framework Layer Receives Request

```python
# app/main.py
app = FastAPI(title="FastAPI Clean Architecture")

# FastAPI automatically:
# - Parses JSON
# - Validates content type
# - Routes to appropriate handler
```

#### 3. Route Handler (Interface Adapter)

```python
# app/api/routes/user.py
@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    user_data: UserCreate,  # Pydantic validates this
    service: UserService = Depends(get_user_service)
):
    """
    Create new user.
    
    At this point:
    - Request is validated by Pydantic (UserCreate schema)
    - Service is injected via dependency injection
    - No business logic here - just delegation
    """
    return service.create_user(user_data)
```

#### 4. Schema Validation (Use Case Layer)

```python
# app/schemas/user.py
class UserCreate(BaseModel):
    email: EmailStr  # Validates email format
    password: str = Field(..., min_length=8)  # Validates password length
    full_name: Optional[str] = None
    
    @validator('password')
    def password_strength(cls, v):
        """Custom validation."""
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain a number')
        return v
```

#### 5. Service Business Logic (Use Case Layer)

```python
# app/services/user_service.py
class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        Business logic for user creation.
        """
        # Business Rule 1: Email must be unique
        existing_user = self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        
        # Business Rule 2: Hash password before storing
        hashed_password = hash_password(user_data.password)
        
        # Business Rule 3: Set default role if not provided
        if not user_data.role_id:
            default_role = self.user_repository.get_default_role()
            user_data.role_id = default_role.id
        
        # Business Rule 4: New users start unverified
        user_data.is_verified = False
        
        # Delegate to repository for data persistence
        new_user = self.user_repository.create(user_data, hashed_password)
        
        # Business Logic: Send welcome email
        # (This could be moved to a background task)
        self._send_welcome_email(new_user.email)
        
        return new_user
    
    def _send_welcome_email(self, email: str):
        """Send welcome email to new user."""
        # Email logic here
        pass
```

#### 6. Repository Data Access (Interface Adapter)

```python
# app/repositories/user_repository.py
class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def create(self, user_data: UserCreate, hashed_password: str) -> User:
        """
        Create user in database.
        
        No business logic here - just data access.
        """
        # Create User model instance
        db_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role_id=user_data.role_id,
            is_verified=False,
            is_active=True
        )
        
        # Add to session
        self.db.add(db_user)
        
        # Commit transaction
        self.db.commit()
        
        # Refresh to get generated ID
        self.db.refresh(db_user)
        
        return db_user
```

#### 7. Model Definition (Domain Layer)

```python
# app/models/user.py
class User(Base):
    """User entity - core business object."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    role_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship("Role", back_populates="users")
```

#### 8. Database Operation (Framework Layer)

```sql
-- SQLAlchemy generates and executes:
INSERT INTO users (email, hashed_password, full_name, role_id, is_active, is_verified, created_at)
VALUES ('john@example.com', '$2b$12$...', 'John Doe', 2, true, false, '2024-01-15 10:30:00');
```

#### 9. Response Transformation

```python
# app/schemas/user.py
class UserResponse(BaseModel):
    """Response schema - what client receives."""
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    role_id: int
    
    class Config:
        from_attributes = True  # Allows creation from ORM model
```

#### 10. Client Receives Response

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": 42,
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "role_id": 2
}
```

### Example 2: User Authentication

Let's trace a login request:

#### 1. Client Request

```http
POST /api/auth/login HTTP/1.1
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

#### 2. Route Handler

```python
# app/api/routes/auth.py
@router.post("/login", response_model=TokenResponse)
def login(
    credentials: LoginRequest,
    service: AuthService = Depends(get_auth_service)
):
    return service.login(credentials.email, credentials.password)
```

#### 3. Authentication Service

```python
# app/services/auth_service.py
class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        token_service: TokenBlacklistService
    ):
        self.user_repository = user_repository
        self.token_service = token_service
    
    def login(self, email: str, password: str) -> dict:
        """Authenticate user and generate tokens."""
        
        # Step 1: Get user by email
        user = self.user_repository.get_by_email(email)
        
        # Step 2: Verify user exists
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        
        # Step 3: Verify password
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        
        # Step 4: Check if account is active
        if not user.is_active:
            raise HTTPException(
                status_code=403,
                detail="Account is inactive"
            )
        
        # Step 5: Generate tokens
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        # Step 6: Return tokens
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
```

#### 4. Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Example 3: Protected Endpoint

Let's trace an authenticated request:

#### 1. Client Request with Token

```http
GET /api/me HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### 2. Route Handler with Authentication

```python
# app/api/routes/me.py
@router.get("/", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user profile.
    
    Authentication happens in dependency (get_current_user).
    """
    return current_user
```

#### 3. Authentication Dependency

```python
# app/api/dependencies.py
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Extract and validate JWT token.
    Get current user from database.
    """
    # Step 1: Extract token
    token = credentials.credentials
    
    # Step 2: Decode and validate token
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: int = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
    
    # Step 3: Get user from database
    repository = UserRepository(db)
    user = repository.get_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    
    return user
```

## Data Transformations

Data changes format as it moves through layers:

### 1. Request → Schema (Pydantic)

```python
# Raw JSON
{"email": "user@example.com", "password": "pass123"}

# Becomes UserCreate object
UserCreate(email="user@example.com", password="pass123")
```

### 2. Schema → Model (SQLAlchemy)

```python
# UserCreate (Pydantic)
user_data = UserCreate(email="user@example.com", password="pass123")

# Becomes User (SQLAlchemy model)
db_user = User(
    email=user_data.email,
    hashed_password=hash_password(user_data.password)
)
```

### 3. Model → Response Schema

```python
# User (SQLAlchemy model)
db_user = User(id=1, email="user@example.com", is_active=True)

# Becomes UserResponse (Pydantic)
response = UserResponse.from_orm(db_user)

# Serialized to JSON
{"id": 1, "email": "user@example.com", "is_active": true}
```

## Error Flow

Errors also flow through layers:

```mermaid
sequenceDiagram
    participant Client
    participant Route as Route Handler
    participant Service as Service Layer
    participant Repo as Repository
    participant FastAPI as FastAPI Exception Handler
    
    Client->>Route: POST /users<br/>{email: "exists@test.com"}
    Route->>Service: create_user(user_data)
    Service->>Repo: get_by_email("exists@test.com")
    Repo-->>Service: User object found
    Service->>Service: ❌ Email exists!
    Service-->>Route: HTTPException(400, "Email exists")
    Route-->>FastAPI: Exception propagates
    FastAPI-->>Client: HTTP 400<br/>{"detail": "Email already exists"}
    
    rect rgb(255, 205, 210)
    Note over Service,FastAPI: Error Flow
    end
```

## Async Flow

Some operations use async/await:

```python
# app/services/email_service.py
class EmailService:
    async def send_verification_email(self, email: str, token: str):
        """Send email asynchronously."""
        await aiosmtplib.send(...)

# app/api/routes/auth.py
@router.post("/register")
async def register(user_data: UserCreate):
    """Async route handler."""
    new_user = service.create_user(user_data)
    
    # Send email asynchronously
    await email_service.send_verification_email(
        new_user.email,
        verification_token
    )
    
    return new_user
```

## Summary

### Key Points

1. **Top to Bottom**: Request flows from outer layers inward
2. **Bottom to Top**: Response flows from inner layers outward
3. **Transformations**: Data changes format at layer boundaries
4. **Independence**: Each layer can be tested independently
5. **Separation**: Business logic (services) separate from data access (repositories)

### Data Flow Principles

- ✅ **One direction**: Dependencies point inward
- ✅ **Clear boundaries**: Each layer has specific responsibility
- ✅ **Loose coupling**: Layers communicate through interfaces
- ✅ **High cohesion**: Related code stays together

### Next Steps

- [Design Patterns](design-patterns.md) - Learn patterns used
- [API Overview](../api/overview.md) - Explore available endpoints
- [Development Guide](../development/best-practices.md) - Best practices
