# Configuration

Learn how to configure the FastAPI Clean Architecture application for different environments.

## Environment Files

The application supports multiple environments (development, testing, production). Each environment has its own configuration file.

### Creating Environment Files

Copy the example environment file to create your environment-specific configurations:

=== "Windows (PowerShell)"
    ```powershell
    Copy-Item .env.example .env.development
    Copy-Item .env.example .env.testing
    Copy-Item .env.example .env.production
    ```

=== "Unix/Linux/macOS"
    ```bash
    cp .env.example .env.development
    cp .env.example .env.testing
    cp .env.example .env.production
    ```

## Environment Variables

### Core Settings

```bash
# Environment (development, testing, or production)
ENVIRONMENT=development

# App URL (for email links)
APP_URL=http://localhost:8000
RESET_PASSWORD_ENDPOINT=/users/reset-password
```

### Security Settings

!!! danger "Important"
    Always generate a new `SECRET_KEY` for production! Never use the default key.

```bash
# Security - Generate with: openssl rand -hex 32
SECRET_KEY=your_super_secret_key_here_change_this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Generate a secure secret key:**

=== "Linux/macOS"
    ```bash
    openssl rand -hex 32
    ```

=== "Windows (PowerShell)"
    ```powershell
    # Use Python
    python -c "import secrets; print(secrets.token_hex(32))"
    ```

=== "Python"
    ```python
    import secrets
    print(secrets.token_hex(32))
    ```

### Database Configuration

Configure your database connection URL:

=== "SQLite (Development)"
    ```bash
    DATABASE_URL=sqlite:///./test.db
    ```

=== "PostgreSQL"
    ```bash
    DATABASE_URL=postgresql://user:password@localhost:5432/dbname
    ```

=== "MySQL"
    ```bash
    DATABASE_URL=mysql://user:password@localhost:3306/dbname
    ```

### Email Configuration (Gmail)

To enable email functionality for OTP and password reset:

```bash
# Gmail SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Use App Password if 2FA enabled
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=Your App Name
```

#### Setting Up Gmail App Password

1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Enable **2-Factor Authentication**
3. Generate an **App Password**: [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
4. Use the generated 16-character password in `SMTP_PASSWORD`

!!! tip "Email Service Alternatives"
    You can use other email services by changing the SMTP settings:
    
    - **SendGrid**: SMTP or API
    - **Mailgun**: SMTP or API
    - **AWS SES**: SMTP or API
    - **Outlook**: `smtp.office365.com:587`

### Email Domain Validation

Restrict user registration to specific email domains:

```bash
# Email Domain Validation (comma-separated)
ACCEPTED_EMAIL_DOMAINS=example.com,yourdomain.com

# Or allow all domains
ACCEPTED_EMAIL_DOMAINS=*
```

### OTP Configuration

Configure One-Time Password settings:

```bash
# OTP Configuration
OTP_EXPIRE_MINUTES=5  # OTP validity duration
OTP_LENGTH=6          # Number of digits in OTP
```

## Setting Active Environment

Specify which environment configuration to use:

=== "Windows (PowerShell)"
    ```powershell
    $env:ENVIRONMENT = "development"  # or "testing", "production"
    ```

=== "Windows (Command Prompt)"
    ```cmd
    set ENVIRONMENT=development
    ```

=== "Unix/Linux/macOS"
    ```bash
    export ENVIRONMENT=development
    ```

!!! note "Default Environment"
    If no `ENVIRONMENT` variable is set, the application defaults to `development`. 
    This command should be run in the same terminal session where you start the application. 

## Complete Configuration Example

Here's a complete `.env.development` file example:

```bash
# Environment
ENVIRONMENT=development

# App Settings
APP_URL=http://localhost:8000
RESET_PASSWORD_ENDPOINT=/users/reset-password

# Security
SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Domain Validation
ACCEPTED_EMAIL_DOMAINS=example.com,mycompany.com

# Database
DATABASE_URL=sqlite:///./test.db

# Gmail SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@example.com
SMTP_PASSWORD=abcd efgh ijkl mnop
SMTP_FROM_EMAIL=noreply@example.com
SMTP_FROM_NAME=FastAPI Clean Architecture

# OTP Configuration
OTP_EXPIRE_MINUTES=5
OTP_LENGTH=6
```

## Production Configuration

For production, use environment variable substitution for sensitive values:

```bash
# .env.production
ENVIRONMENT=production
SECRET_KEY=${PROD_SECRET_KEY}
DATABASE_URL=${PROD_DATABASE_URL}
SMTP_PASSWORD=${PROD_SMTP_PASSWORD}
```

Then set actual values on your server:

```bash
export PROD_SECRET_KEY="your_actual_secret_key"
export PROD_DATABASE_URL="postgresql://user:pass@host/db"
export PROD_SMTP_PASSWORD="your_actual_password"
```

## Verification

To verify your configuration is loaded correctly, check the application logs on startup:

```
INFO:app:Application starting in development environment
INFO:app:Database URL: sqlite:///./test.db
INFO:app:SMTP configured: smtp.gmail.com:587
```

## What's Next?

After configuration, proceed to:

- [Data Setup](data-setup.md) - Configure initial users and permissions
- [Database Migrations](../database/migrations.md) - Set up database schema

## Troubleshooting

### Environment Variables Not Loading

**Problem:** Configuration not being read

**Solution:**

- Ensure `.env.{ENVIRONMENT}` file exists
- Check file naming (must be `.env.development`, not `.env-development`)
- Verify `ENVIRONMENT` variable is set correctly

### Database Connection Errors

**Problem:** Cannot connect to database

**Solution:**

- Check `DATABASE_URL` format
- Ensure database server is running (for PostgreSQL/MySQL)
- Verify database credentials

See [Common Issues](../troubleshooting/common-issues.md) for more help.
