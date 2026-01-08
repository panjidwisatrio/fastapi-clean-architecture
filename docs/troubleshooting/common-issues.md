# Common Issues

Solutions to frequently encountered problems.

## Installation Issues

### Virtual Environment Not Activating

**Problem**: Cannot activate virtual environment

**Solution**:

Windows:
```powershell
.venv\Scripts\activate
```

Linux/Mac:
```bash
source .venv/bin/activate
```

### Module Not Found Errors

**Problem**: `ModuleNotFoundError: No module named 'app'`

**Solution**:
1. Ensure virtual environment is activated
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run from project root directory

## Database Issues

### Cannot Connect to Database

**Problem**: `could not connect to server: Connection refused`

**Solution**:
1. Check if PostgreSQL is running:
   ```bash
   # Windows
   sc query postgresql-x64-15
   
   # Linux
   sudo systemctl status postgresql
   ```

2. Verify `DATABASE_URL` in `.env`:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   ```

3. Check database exists:
   ```bash
   psql -U postgres -l
   ```

### Migration Errors

**Problem**: `Can't locate revision identified by 'abc123'`

**Solution**:

Reset migrations:
```bash
# Delete all migration files except __init__.py
rm alembic/versions/*.py

# Create new initial migration
alembic revision --autogenerate -m "initial migration"

# Apply migration
alembic upgrade head
```

### Table Already Exists

**Problem**: `relation "users" already exists`

**Solution**:

Option 1 - Mark as applied:
```bash
alembic stamp head
```

Option 2 - Drop and recreate:
```bash
# Backup data first!
alembic downgrade base
alembic upgrade head
```

## Authentication Issues

### JWT Token Invalid

**Problem**: `Could not validate credentials`

**Solution**:
1. Check token hasn't expired (30 minutes default)
2. Verify `SECRET_KEY` matches between encoding/decoding
3. Check token format: `Bearer <token>`

### Permission Denied

**Problem**: `403 Forbidden: Insufficient permissions`

**Solution**:
1. Verify user has required role
2. Check role has required permissions in `permissions.json`
3. Restart app after changing permissions

## Email Issues

### SMTP Authentication Failed

**Problem**: `SMTPAuthenticationError`

**Solution**:

For Gmail:
1. Enable "Less secure app access" OR
2. Use App Password:
   - Go to Google Account settings
   - Security → App passwords
   - Generate password for "Mail"
   - Use this in `SMTP_PASSWORD`

Verify SMTP settings:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com
```

### Email Not Sending

**Problem**: Emails not being delivered

**Solution**:
1. Check logs: `logs/app.log`
2. Verify SMTP credentials
3. Check firewall allows port 587
4. Test with different email provider

## Alembic Issues

### Alembic Command Not Found

**Problem**: `alembic: command not found`

**Solution**:
```bash
# Activate virtual environment first
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Verify installation
pip list | grep alembic

# Reinstall if needed
pip install alembic
```

### Import Errors in Migrations

**Problem**: `ModuleNotFoundError` in migration files

**Solution**:

Check `alembic/env.py` has correct import path:
```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import Base
from app.models import user, role, permission  # Import all models
```

## API Issues

### CORS Errors

**Problem**: `Access to XMLHttpRequest has been blocked by CORS policy`

**Solution**:

Update `ALLOWED_ORIGINS` in `.env`:
```env
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend.com
```

Or in `app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 422 Validation Error

**Problem**: `Unprocessable Entity` on valid-looking data

**Solution**:
1. Check Swagger docs for exact schema: `/docs`
2. Verify field names match exactly
3. Check required fields aren't missing
4. Validate data types (string vs integer, etc.)

Example error:
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

## Performance Issues

### Slow API Responses

**Problem**: Endpoints taking too long

**Solution**:
1. Enable query logging:
   ```python
   engine = create_engine(DATABASE_URL, echo=True)
   ```

2. Add database indexes:
   ```python
   email = Column(String, unique=True, index=True)
   ```

3. Use pagination:
   ```python
   @router.get("/users")
   def list_users(skip: int = 0, limit: int = 100):
       pass
   ```

4. Optimize queries (use `joinedload`):
   ```python
   db.query(User).options(joinedload(User.role)).all()
   ```

### High Memory Usage

**Problem**: Application using too much memory

**Solution**:
1. Reduce Gunicorn workers
2. Configure database connection pool:
   ```python
   engine = create_engine(
       DATABASE_URL,
       pool_size=5,
       max_overflow=0
   )
   ```

## Logging Issues

### Log File Not Created

**Problem**: `logs/app.log` doesn't exist

**Solution**:
```bash
# Create logs directory
mkdir logs

# Verify permissions
chmod 755 logs

# Check logging configuration in app/core/logging.py
```

### Too Many Log Files

**Problem**: Logs filling up disk space

**Solution**:

Configure rotating file handler:
```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10_000_000,  # 10MB
    backupCount=5         # Keep 5 old files
)
```

## Development Issues

### Hot Reload Not Working

**Problem**: Changes not reflected without restart

**Solution**:
```bash
# Use --reload flag
uvicorn app.main:app --reload

# Or use environment variable
ENVIRONMENT=development uvicorn app.main:app
```

### Import Errors

**Problem**: `ImportError: cannot import name 'X' from 'app.Y'`

**Solution**:
1. Check for circular imports
2. Verify file exists
3. Check `__init__.py` in package
4. Use absolute imports:
   ```python
   from app.models.user import User  # Good
   from .models import User          # Can cause issues
   ```

## Still Having Issues?

1. Check [FAQ](faq.md)
2. Review [Configuration Guide](../getting-started/configuration.md)
3. Enable debug logging:
   ```env
   LOG_LEVEL=DEBUG
   ```
4. Open GitHub issue with:
   - Error message
   - Steps to reproduce
   - Environment (OS, Python version)
   - Relevant logs
