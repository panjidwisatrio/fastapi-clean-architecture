# Development Best Practices

Guidelines and best practices for development.

## Code Style

### Follow PEP 8

```python
# Good
def create_user(email: str, password: str) -> User:
    pass

# Bad
def CreateUser(email,password):
    pass
```

### Use Type Hints

```python
from typing import Optional, List

def get_users(skip: int = 0, limit: int = 100) -> List[User]:
    pass
```

### Write Docstrings

```python
def authenticate_user(email: str, password: str) -> User:
    """
    Authenticate user with email and password.
    
    Args:
        email: User email address
        password: Plain text password
        
    Returns:
        Authenticated user object
        
    Raises:
        HTTPException: If credentials are invalid
    """
    pass
```

## Architecture

### Keep Business Logic in Services

```python
# Good - Business logic in service
class UserService:
    def create_user(self, data: UserCreate) -> User:
        if self.repo.get_by_email(data.email):
            raise HTTPException(400, "Email exists")
        return self.repo.create(data)

# Bad - Business logic in route
@router.post("/users")
def create_user(data: UserCreate):
    user = db.query(User).filter_by(email=data.email).first()
    if user:
        raise HTTPException(400, "Email exists")
    # ...
```

### Use Repository Pattern

```python
# Good - Abstract data access
class UserRepository:
    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

# Bad - Direct database access in service
class UserService:
    def get_user(self, email: str):
        return self.db.query(User).filter(User.email == email).first()
```

### Dependency Injection

```python
# Good - Inject dependencies
def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))

@router.get("/users")
def list_users(service: UserService = Depends(get_user_service)):
    return service.get_all()
```

## Error Handling

### Use HTTP Exceptions

```python
from fastapi import HTTPException

def get_user(user_id: int) -> User:
    user = self.repo.get_by_id(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user
```

### Validate Input

```python
from pydantic import EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1)
```

## Database

### Use Migrations

Always use Alembic for schema changes:

```bash
alembic revision --autogenerate -m "add field"
alembic upgrade head
```

Never modify models directly in production!

### Index Important Columns

```python
class User(Base):
    email = Column(String, unique=True, index=True)  # ✅ Indexed
    created_at = Column(DateTime, index=True)        # ✅ For queries
```

## Security

### Hash Passwords

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])
hashed = pwd_context.hash(plain_password)
```

### Validate Permissions

```python
@router.delete("/users/{id}")
def delete_user(
    id: int,
    current_user: User = Depends(get_current_user_with_permission("user:delete"))
):
    pass
```

### Use Environment Variables

```python
# Good
SECRET_KEY = os.getenv("SECRET_KEY")

# Bad
SECRET_KEY = "hardcoded_secret"  # ❌ Never do this!
```

## Testing

### Write Tests for Business Logic

```python
def test_create_user_duplicate_email():
    service = UserService(mock_repo)
    
    # First user
    service.create_user(UserCreate(email="test@test.com"))
    
    # Duplicate should raise error
    with pytest.raises(HTTPException) as exc:
        service.create_user(UserCreate(email="test@test.com"))
    
    assert exc.value.status_code == 400
```

### Mock External Dependencies

```python
from unittest.mock import Mock

def test_send_email():
    mock_email_service = Mock()
    service = UserService(repo, mock_email_service)
    
    service.register_user(data)
    
    mock_email_service.send_welcome_email.assert_called_once()
```

## Documentation

### Update Documentation

When adding features:
1. Update API docs
2. Update README
3. Add examples
4. Update changelog

### Comment Complex Logic

```python
def complex_calculation(data):
    # Calculate weighted average based on user preferences
    # Algorithm from: https://example.com/paper.pdf
    weighted_sum = sum(item.value * item.weight for item in data)
    total_weight = sum(item.weight for item in data)
    return weighted_sum / total_weight if total_weight > 0 else 0
```

## Git Workflow

### Commit Messages

```
feat: add user profile endpoint
fix: resolve token expiry issue
docs: update installation guide
refactor: simplify auth service
test: add user service tests
```

### Branch Naming

```
feature/user-profile
bugfix/token-expiry
hotfix/security-patch
```

## Code Review

### Review Checklist

- [ ] Follows architecture patterns
- [ ] Has tests
- [ ] Documentation updated
- [ ] No hardcoded secrets
- [ ] Error handling present
- [ ] Type hints used
- [ ] Follows PEP 8

## Performance

### Use Async Where Possible

```python
# Good - Async for I/O operations
@router.get("/users")
async def list_users():
    return await service.get_all()

# Good - Sync for CPU-bound
@router.post("/analyze")
def analyze_data(data: List[int]):
    return sum(data) / len(data)
```

### Optimize Database Queries

```python
# Good - Eager loading
users = db.query(User).options(joinedload(User.role)).all()

# Bad - N+1 queries
users = db.query(User).all()
for user in users:
    print(user.role.name)  # Separate query each time
```

See [Architecture Overview](../architecture/overview.md) for more details.
