# FastAPI Clean Architecture

**A modern, production-ready web application template built with FastAPI following clean architecture principles**
{: .text-center}

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95.2-green)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
{: .text-center}

[Get Started](#quick-start){ .md-button .md-button--primary }
[View on GitHub](https://github.com/panjidwisatrio/fastapi-clean-architecture){ .md-button }
{: .text-center}

---

## ✨ Overview

This template provides a robust foundation for building scalable REST APIs with authentication, authorization, and a comprehensive feature set. It implements clean architecture principles to ensure maintainability, testability, and independence from frameworks.

## 🎯 Key Features

<div class="grid cards" markdown>

-   :material-shield-lock:{ .lg .middle } __Authentication & Authorization__

    ---

    JWT-based authentication with role-based access control (RBAC) and permission-based authorization

-   :material-database:{ .lg .middle } __Database Migrations__

    ---

    Alembic integration for version-controlled database schema management

-   :material-email:{ .lg .middle } __Email Services__

    ---

    SMTP email integration with async sending and OTP verification

-   :material-api:{ .lg .middle } __RESTful API__

    ---

    Automatic OpenAPI/Swagger documentation with request/response validation

-   :material-code-tags:{ .lg .middle } __Code Generation__

    ---

    CLI tool to generate complete CRUD operations in seconds

-   :material-layers:{ .lg .middle } __Clean Architecture__

    ---

    Separation of concerns with distinct layers for maintainability

</div>

## 🚀 Quick Start

Get up and running in 5 minutes:

```bash
# Clone the repository
git clone https://github.com/panjidwisatrio/fastapi-clean-architecture.git
cd fastapi-clean-architecture

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Initialize data
python .\module\initiate_data\initiate.py

# Configure environment
cp .env.example .env.development

# Run the application
uvicorn app.main:app --reload

# Run database migrations
alembic revision --autogenerate -m "initial migration"
alembic upgrade head

```

Visit [http://localhost:8000/docs](http://localhost:8000/docs) to see the interactive API documentation!

!!! tip "Next Steps"
    - Read the [Installation Guide](getting-started/installation.md) for detailed setup
    - Configure your [Data Files](getting-started/data-setup.md) for initial users and permissions
    - Learn about [Database Migrations](database/migrations.md)

## 📚 Documentation Structure

<div class="grid" markdown>

=== "Getting Started"
    - [Installation](getting-started/installation.md)
    - [Configuration](getting-started/configuration.md)
    - [Data Setup](getting-started/data-setup.md)
    - [First Steps](getting-started/first-steps.md)

=== "Architecture"
    - [Overview](architecture/overview.md)
    - [Layers](architecture/layers.md)
    - [Data Flow](architecture/data-flow.md)
    - [Design Patterns](architecture/design-patterns.md)

=== "Development"
    - [Code Generation](development/code-generation.md)
    - [Testing](development/testing.md)
    - [Best Practices](development/best-practices.md)

=== "Deployment"
    - [Production](deployment/production.md)
    - [Docker](deployment/docker.md)
    - [Cloud Platforms](deployment/cloud-platforms.md)

</div>

## 🏗️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | FastAPI |
| **Database** | SQLAlchemy (PostgreSQL/MySQL/SQLite) |
| **Migrations** | Alembic |
| **Authentication** | JWT (python-jose) |
| **Validation** | Pydantic |
| **Email** | aiosmtplib |
| **Server** | Uvicorn |

## 🎓 Learn More

- [Architecture Overview](architecture/overview.md) - Understand the clean architecture implementation
- [API Documentation](api/overview.md) - Explore available endpoints
- [Code Generation](development/code-generation.md) - Learn to use the CLI tool
- [Troubleshooting](troubleshooting/common-issues.md) - Common issues and solutions

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](contributing/guidelines.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [License](about/license.md) page for details.

## 🌟 Support

- :fontawesome-brands-github: [GitHub Issues](https://github.com/panjidwisatrio/fastapi-clean-architecture/issues)
- :fontawesome-brands-twitter: [Twitter](https://twitter.com/panjisatrio1410)
- :material-email: Email: panjisatrio888@gmail.com

---


**Made with ❤️ using FastAPI and Clean Architecture principles**
{: .text-center}