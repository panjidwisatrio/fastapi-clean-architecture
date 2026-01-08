# Frequently Asked Questions

Common questions about FastAPI Clean Architecture.

## General

### What is Clean Architecture?

Clean Architecture is a software design pattern that separates concerns into distinct layers, making code more maintainable, testable, and independent of frameworks and databases.

Learn more: [Architecture Overview](../architecture/overview.md)

### What Python version is required?

Python 3.11 or higher is recommended. The project uses modern Python features like type hints and async/await.

Check your version:
```bash
python --version
```

### Can I use a different database?

Yes! The project supports PostgreSQL, MySQL, and SQLite through SQLAlchemy.

Change `DATABASE_URL` in `.env`:

```env
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# MySQL
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/dbname

# SQLite (development only)
DATABASE_URL=sqlite:///./app.db
```

## Authentication

### How long do JWT tokens last?

Access tokens expire after 30 minutes by default. Configure in `.env`:

```env
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### How do I change the default admin password?

1. Login as admin with default credentials
2. Call `PUT /api/v1/me/password` to change password
3. Or update directly in database:
   ```python
   from app.core.security import get_password_hash
   new_hash = get_password_hash("new_password")
   ```

### What is the difference between roles and permissions?

- **Roles**: Groups of users (e.g., Admin, User)
- **Permissions**: Specific actions (e.g., user:create, user:delete)
- Roles contain multiple permissions
- Users are assigned roles

See [Roles & Permissions](../api/roles-permissions.md)

### Can users have multiple roles?

Currently, users have one role. To support multiple roles:

1. Change `user.py` model to many-to-many relationship
2. Update authentication logic
3. Modify permission checking

## Development

### How do I add a new endpoint?

1. Define schema in `app/schemas/`
2. Create service in `app/services/`
3. Add route in `app/api/routes/`
4. Test with `/docs`

See [Code Generation](../development/code-generation.md) for automation.

### Where are API docs?

Interactive Swagger UI: `http://localhost:8000/docs`

Alternative ReDoc: `http://localhost:8000/redoc`

### How do I run tests?

```bash
pytest

# With coverage
pytest --cov=app

# Specific file
pytest app/tests/test_auth.py
```

See [Testing Guide](../development/testing.md)

### How do I debug the application?

1. **Swagger UI**: Test endpoints at `/docs`
2. **Logs**: Check `logs/app.log`
3. **VS Code Debugger**: Use launch configuration
4. **Print Debugging**: Add logging statements

See [Debugging Guide](../development/debugging.md)

## Database

### How do I create migrations?

```bash
# Auto-generate migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

See [Database Migrations](../database/migrations.md)

### What is the initial admin user?

Default credentials (change immediately!):

- Email: `admin@example.com`
- Password: `admin123`

### How do I reset the database?

**Warning**: This deletes all data!

```bash
# Downgrade to empty state
alembic downgrade base

# Upgrade to latest
alembic upgrade head

# Re-seed initial data
python -m app.core.init_db
```

### Can I use MongoDB?

Not directly. The project uses SQLAlchemy ORM for relational databases. For MongoDB:

1. Replace SQLAlchemy with Motor/Beanie
2. Rewrite models
3. Update repositories

This requires significant changes.

## Deployment

### How do I deploy to production?

See [Production Deployment](../deployment/production.md) for complete guide.

Key steps:
1. Set `ENVIRONMENT=production`
2. Use strong `SECRET_KEY`
3. Configure production database
4. Use Gunicorn + Nginx
5. Enable HTTPS

### What about Docker?

Yes! See [Docker Deployment](../deployment/docker.md).

Quick start:
```bash
docker-compose up -d
```

### Which cloud platform should I use?

Depends on your needs:

- **Heroku**: Easiest for beginners
- **DigitalOcean**: Good balance
- **AWS/GCP/Azure**: Enterprise scale

See [Cloud Platforms](../deployment/cloud-platforms.md)

## Email

### Why aren't emails sending?

Common causes:

1. **Wrong SMTP settings**: Check `.env`
2. **Gmail blocking**: Use App Password
3. **Firewall**: Allow port 587
4. **Email doesn't exist**: Check recipient

See [Email Issues](common-issues.md#email-issues)

### Can I use SendGrid/Mailgun?

Yes! Update SMTP settings in `.env`:

**SendGrid**:
```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your_sendgrid_api_key
```

**Mailgun**:
```env
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@your-domain.mailgun.org
SMTP_PASSWORD=your_mailgun_password
```

## OTP (One-Time Password)

### How long is OTP valid?

5 minutes by default. Configure in `app/services/otp_service.py`:

```python
otp_expires = datetime.utcnow() + timedelta(minutes=5)
```

### Can I use OTP for 2FA?

The OTP system is for password reset. For 2FA, you need to:

1. Install `pyotp` library
2. Implement TOTP generation
3. Add 2FA enable/disable endpoints
4. Require OTP during login

## Performance

### Why is my API slow?

Common causes:

1. **No database indexes**: Add to frequently queried fields
2. **N+1 queries**: Use `joinedload()`
3. **No pagination**: Limit results
4. **Debug mode**: Set `ENVIRONMENT=production`

See [Best Practices](../development/best-practices.md)

### How many requests can it handle?

Depends on:
- Server resources
- Database performance
- Query complexity
- Number of workers

Benchmark with `wrk` or `ab`:
```bash
ab -n 1000 -c 10 http://localhost:8000/api/v1/health
```

## Security

### Is it production-ready?

Yes, with proper configuration:

- ✅ Password hashing (bcrypt)
- ✅ JWT authentication
- ✅ Role-based access control
- ✅ Input validation (Pydantic)
- ✅ SQL injection protection (SQLAlchemy)
- ⚠️ Rate limiting (not included, add separately)
- ⚠️ HTTPS (configure in Nginx/cloud platform)

### Should I use this for my project?

This is a **template/boilerplate**. Great for:

- Learning Clean Architecture
- Starting new FastAPI projects
- Understanding best practices
- Prototyping applications

Customize for your specific needs!

## Contributing

### How can I contribute?

See [Contributing Guidelines](../contributing/guidelines.md)

1. Fork repository
2. Create feature branch
3. Make changes
4. Submit pull request

### Where do I report bugs?

Open an issue on GitHub with:
- Description
- Steps to reproduce
- Expected vs actual behavior
- Environment details

## Still Have Questions?

- Check [Common Issues](common-issues.md)
- Review [Documentation](../index.md)
- Open GitHub Issue
- Read the code! It's well-documented
