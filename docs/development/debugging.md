# Debugging Guide

Tools and techniques for debugging the application.

## Debugging Tools

### 1. FastAPI Swagger UI

Interactive API documentation with built-in testing:

```
http://127.0.0.1:8000/docs
```

- Test endpoints directly
- View request/response
- Check validation errors

### 2. Application Logs

Check logs for detailed information:

```
logs/app.log
```

Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

### 3. VS Code Debugger

`.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload"],
      "jinja": true
    }
  ]
}
```

Set breakpoints and step through code.

### 4. Database Inspection

Connect to database:

```bash
psql -U postgres -d fastapi_db
```

Inspect tables:

```sql
SELECT * FROM users;
SELECT * FROM roles;
```

## Common Debugging Scenarios

### Authentication Issues

1. Check token in Swagger authorize button
2. Verify token expiry
3. Check user permissions
4. Review logs for auth errors

### Database Issues

1. Verify connection string in `.env`
2. Check if migrations are applied
3. Inspect database directly
4. Review SQLAlchemy logs

### Import Errors

1. Verify virtual environment is activated
2. Check `requirements.txt` installed
3. Verify Python path
4. Check for circular imports

## Debug Mode

Enable debug mode in `.env`:

```env
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

This provides:
- Detailed error messages
- Stack traces
- SQL query logging
- Request/response logging

## Profiling

Use FastAPI's built-in profiler:

```python
@router.get("/slow")
async def slow_endpoint():
    import time
    time.sleep(1)
    return {"status": "slow"}
```

Check response time in Swagger UI.

See [Troubleshooting](../troubleshooting/common-issues.md) for common issues.
