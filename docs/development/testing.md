# Testing Guide

Comprehensive testing strategies and examples.

## Test Structure

```
tests/
├── test_auth.py       # Authentication tests
├── test_users.py      # User management tests
├── test_services.py   # Service layer tests
└── conftest.py        # Pytest fixtures
```

## Running Tests

### All Tests

```bash
pytest
```

### With Coverage

```bash
pytest --cov=app --cov-report=html
```

### Specific Test File

```bash
pytest tests/test_auth.py
```

## Test Examples

### Unit Test Example

```python
def test_create_user(db_session):
    service = UserService(UserRepository(db_session))
    
    user = service.create_user(
        email="test@example.com",
        password="Test123!",
        full_name="Test User"
    )
    
    assert user.email == "test@example.com"
    assert user.is_active == True
```

### Integration Test Example

```python
def test_register_endpoint(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "Test123!",
            "full_name": "Test User"
        }
    )
    
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
```

## Fixtures

```python
# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)
```

## Best Practices

- Test business logic in services
- Use in-memory SQLite for speed
- Mock external dependencies
- Test error cases
- Aim for >80% coverage

See `app/tests/` for examples.
