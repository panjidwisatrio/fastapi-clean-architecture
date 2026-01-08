# Contributing Guidelines

Thank you for considering contributing to FastAPI Clean Architecture!

## Getting Started

1. **Fork** the repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/yourusername/fastapi-clean-architecture.git
   cd fastapi-clean-architecture
   ```
3. **Create virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Development Workflow

### 1. Create a Branch

Create a descriptive branch name:

```bash
# Feature
git checkout -b feature/user-profile-photo

# Bug fix
git checkout -b fix/email-validation-error

# Documentation
git checkout -b docs/update-readme
```

### 2. Make Changes

Follow our [Code Standards](#code-standards).

### 3. Test Your Changes

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

### 4. Commit Changes

Write clear commit messages:

```bash
git add .
git commit -m "feat: add user profile photo upload"
```

#### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Examples:
```
feat: add password reset endpoint
fix: resolve JWT token expiration issue
docs: update installation instructions
refactor: optimize database queries in user repository
test: add unit tests for auth service
```

### 5. Push Changes

```bash
git push origin feature/user-profile-photo
```

### 6. Submit Pull Request

1. Go to GitHub repository
2. Click "Pull Request"
3. Select your branch
4. Fill in the template:
   - Description of changes
   - Related issues
   - Testing done
   - Screenshots (if UI changes)

## Code Standards

### Python Style Guide

Follow [PEP 8](https://pep8.org/):

```python
# Good
def calculate_total_price(items: list[Item]) -> float:
    """Calculate total price from list of items."""
    return sum(item.price for item in items)

# Bad
def calc(x):
    return sum([i.price for i in x])
```

### Type Hints

Always use type hints:

```python
# Good
def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

# Bad
def get_user(db, user_id):
    return db.query(User).filter(User.id == user_id).first()
```

### Docstrings

Use docstrings for functions and classes:

```python
def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate user by email and password.

    Args:
        db: Database session
        email: User email address
        password: Plain text password

    Returns:
        User object if authentication successful, None otherwise
    """
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
```

### Import Order

Follow standard import order:

```python
# 1. Standard library
import os
from datetime import datetime

# 2. Third-party
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# 3. Local
from app.core.database import get_db
from app.schemas.user import UserCreate
```

### Clean Architecture

Maintain layer separation:

```python
# ✅ Good: Repository accesses database
class UserRepository:
    def create(self, db: Session, user_data: dict) -> User:
        user = User(**user_data)
        db.add(user)
        db.commit()
        return user

# ✅ Good: Service uses repository
class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def register_user(self, db: Session, data: UserCreate) -> User:
        hashed_password = get_password_hash(data.password)
        user_data = {**data.dict(), "hashed_password": hashed_password}
        return self.user_repo.create(db, user_data)

# ❌ Bad: Route directly accesses database
@router.post("/users")
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    user = User(**data.dict())
    db.add(user)
    db.commit()
    return user
```

## Testing Requirements

### Write Tests

All new features must include tests:

```python
def test_create_user(client, db):
    """Test user creation endpoint."""
    response = client.post("/api/v1/users", json={
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
```

### Test Coverage

Maintain test coverage above 80%:

```bash
pytest --cov=app --cov-report=term-missing
```

### Test Types

Include different test types:

- **Unit tests**: Test individual functions
- **Integration tests**: Test API endpoints
- **Repository tests**: Test database operations

## Documentation

### Code Documentation

- Add docstrings to functions
- Comment complex logic
- Update README if needed
- Add examples for new features

### API Documentation

Update Swagger docs by adding proper schemas:

```python
@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Create new user.
    
    - **email**: Unique email address
    - **password**: Strong password (min 8 chars)
    - **full_name**: User's full name
    """
    # Implementation
```

## Pull Request Guidelines

### Before Submitting

- [ ] Code follows style guide
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No merge conflicts

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #123

## Testing
How was this tested?

## Screenshots
If applicable
```

### Review Process

1. Automated tests run on PR
2. Maintainer reviews code
3. Address feedback
4. Merge when approved

## Code Review Guidelines

### For Contributors

- Be receptive to feedback
- Explain your reasoning
- Keep PRs focused and small
- Respond promptly

### For Reviewers

- Be respectful and constructive
- Explain suggestions clearly
- Approve when standards met
- Test changes locally if needed

## Areas for Contribution

### High Priority

- [ ] Rate limiting middleware
- [ ] WebSocket support
- [ ] Two-factor authentication
- [ ] API versioning
- [ ] More comprehensive tests

### Documentation

- [ ] Video tutorials
- [ ] Architecture diagrams
- [ ] Code examples
- [ ] Translation to other languages

### Nice to Have

- [ ] GraphQL support
- [ ] File upload handling
- [ ] Caching layer
- [ ] Background task queue
- [ ] Audit logging

## Getting Help

- **Questions**: Open GitHub Discussion
- **Bugs**: Open GitHub Issue
- **Security**: Email maintainers privately
- **Chat**: Join Discord/Slack (if available)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors are listed in:
- README.md
- CONTRIBUTORS.md
- GitHub contributors page

Thank you for helping improve FastAPI Clean Architecture! 🎉
