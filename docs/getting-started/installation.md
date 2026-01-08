# Installation Guide

This guide will walk you through the complete installation process of FastAPI Clean Architecture.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **pip** - Python package installer (usually comes with Python)
- **PostgreSQL/MySQL/SQLite** - Database (SQLite works out of the box for development)
- **Git** - Version control system

!!! tip "Recommended Tools"
    - **Virtual Environment** - `.venv` or `virtualenv` for isolated Python environments
    - **Postman** or **Thunder Client** - For API testing
    - **VS Code** - With Python extension for better development experience

## Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/fastapi-clean-architecture.git
cd fastapi-clean-architecture
```

## Step 2: Create Virtual Environment

Creating a virtual environment isolates your project dependencies.

=== "Windows (PowerShell)"
    ```powershell
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    ```

=== "Windows (Command Prompt)"
    ```cmd
    python -m venv .venv
    .\.venv\Scripts\activate.bat
    ```

=== "Unix/Linux/macOS"
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

You should see `(.venv)` in your terminal prompt, indicating the virtual environment is active.

## Step 3: Install Dependencies

Install all required Python packages:

```bash
pip install -r requirements.txt
```

This will install:

- FastAPI and Uvicorn
- SQLAlchemy and Alembic
- Pydantic and validation libraries
- Authentication libraries (JWT, passlib)
- Email libraries (aiosmtplib)
- MkDocs and Material theme (for documentation)
- And more...

!!! note "Installation Time"
    Installation may take 2-5 minutes depending on your internet speed.

## Step 4: Verify Installation

Verify that all dependencies are installed correctly:

```bash
pip list
```

You should see FastAPI, SQLAlchemy, Alembic, and other packages listed.

## What's Next?

After installation, proceed to:

1. [Configuration](configuration.md) - Set up environment variables
2. [Data Setup](data-setup.md) - Configure initial data files
3. [First Steps](first-steps.md) - Run your first API request

## Troubleshooting

### Virtual Environment Issues

**Problem:** Cannot activate virtual environment on Windows

**Solution:**
```powershell
# Enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### pip Installation Fails

**Problem:** Package installation errors

**Solution:**
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Try installing again
pip install -r requirements.txt
```

### Python Version Issues

**Problem:** Python version is too old

**Solution:**
- Download and install Python 3.8 or higher from [python.org](https://www.python.org/downloads/)
- Make sure to check "Add Python to PATH" during installation

## Need Help?

If you encounter issues during installation:

- Check the [Common Issues](../troubleshooting/common-issues.md) page
- Review the [FAQ](../troubleshooting/faq.md)
- Open an issue on [GitHub](https://github.com/panjidwisatrio/fastapi-clean-architecture/issues)
