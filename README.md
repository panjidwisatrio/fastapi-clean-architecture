# FastAPI Clean Architecture

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95.2-green)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A modern, production-ready web application template built with FastAPI following clean architecture principles.**

[📚 Full Documentation](https://panjidwisatrio.github.io/fastapi-clean-architecture/) • [🚀 Quick Start](#quick-start) • [✨ Features](#features)

</div>

---

## 🎯 Overview

This template provides a robust foundation for building scalable REST APIs with:

- ✅ Clean Architecture implementation
- ✅ JWT-based authentication & RBAC
- ✅ Database migrations with Alembic
- ✅ Automatic API documentation
- ✅ Email services (OTP, password reset)
- ✅ CLI code generator
- ✅ Comprehensive documentation

## ✨ Features

- **🔐 Authentication & Authorization** - JWT tokens, RBAC, permission-based access control
- **👤 User Management** - Registration, login, profile management, password reset
- **📧 Email Services** - SMTP integration with async sending, OTP verification
- **🗄️ Database** - SQLAlchemy ORM, Alembic migrations, multiple DB support
- **📝 API** - RESTful design, automatic OpenAPI/Swagger docs, Pydantic validation
- **🤖 Code Generation** - CLI tool to generate complete CRUD operations
- **📚 Documentation** - Comprehensive docs with MkDocs Material

## 🚀 Quick Start

```bash
# 1. Clone repository
git clone https://github.com/panjidwisatrio/fastapi-clean-architecture.git
cd fastapi-clean-architecture

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env.development
# Edit .env.development with your settings

# 5. Setup database
alembic revision --autogenerate -m "initial migration"
alembic upgrade head

# 6. Run application
uvicorn app.main:app --reload
```

Visit [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API documentation!

## 📚 Documentation

Complete documentation is available at: **[https://panjidwisatrio.github.io/fastapi-clean-architecture/](https://panjidwisatrio.github.io/fastapi-clean-architecture/)**

### Quick Links

- [Installation Guide](https://panjidwisatrio.github.io/fastapi-clean-architecture/getting-started/installation/)
- [Configuration](https://panjidwisatrio.github.io/fastapi-clean-architecture/getting-started/configuration/)
- [Data Setup](https://panjidwisatrio.github.io/fastapi-clean-architecture/getting-started/data-setup/)
- [Database Migrations](https://panjidwisatrio.github.io/fastapi-clean-architecture/database/migrations/)
- [Architecture Overview](https://panjidwisatrio.github.io/fastapi-clean-architecture/architecture/overview/)
- [Code Generation](https://panjidwisatrio.github.io/fastapi-clean-architecture/development/code-generation/)
- [Troubleshooting](https://panjidwisatrio.github.io/fastapi-clean-architecture/troubleshooting/common-issues/)

### Build Documentation Locally

```bash
# Serve documentation locally
mkdocs serve

# Build static site
mkdocs build
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) to view documentation.

## 📁 Project Structure

```
fastapi-clean-architecture/
├── alembic/                    # Database migrations
├── app/
│   ├── api/                    # API routes and dependencies
│   ├── core/                   # Core configuration
│   ├── models/                 # Database models
│   ├── repositories/           # Data access layer
│   ├── schemas/                # Pydantic schemas
│   ├── services/               # Business logic
│   ├── data/                   # Initial data files
│   └── main.py                 # Application entry point
├── docs/                       # MkDocs documentation
├── module/                     # Code generation CLI
├── requirements.txt            # Python dependencies
├── mkdocs.yml                  # Documentation config
└── alembic.ini                 # Alembic config
```

## 🏗️ Technology Stack

| Component | Technology |
|-----------|-----------|
| Framework | FastAPI |
| Database ORM | SQLAlchemy |
| Migrations | Alembic |
| Authentication | JWT (python-jose) |
| Validation | Pydantic |
| Email | aiosmtplib |
| Server | Uvicorn |
| Documentation | MkDocs Material |

## 🤖 Code Generator

Generate complete CRUD operations with a single command:

```bash
# Generate model, schema, repository, service, and routes
python module/generate.py crud Product --fields "name:str,price:float,stock:int"

# Generate only specific components
python module/generate.py model Product --fields "name:str,price:float"
python module/generate.py service Product
python module/generate.py route Product
```

[Learn more about Code Generation →](https://panjidwisatrio.github.io/fastapi-clean-architecture/development/code-generation/)

## 📖 API Documentation

Once running, access the interactive API documentation:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Example: Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "Admin@123456"
  }'
```

[View full API documentation →](https://panjidwisatrio.github.io/fastapi-clean-architecture/api/overview/)

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest app/tests/test_env.py
```

## 🚀 Deployment

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t fastapi-app .
docker run -p 8000:8000 --env-file .env.production fastapi-app
```

[Full deployment guide →](https://panjidwisatrio.github.io/fastapi-clean-architecture/deployment/production/)

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](https://panjidwisatrio.github.io/fastapi-clean-architecture/contributing/guidelines/).

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and ORM
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [Alembic](https://alembic.sqlalchemy.org/) - Database migrations
- [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) - Documentation theme

## 📞 Support

- 📖 [Documentation](https://panjidwisatrio.github.io/fastapi-clean-architecture/)
- 🐛 [Issue Tracker](https://github.com/panjidwisatrio/fastapi-clean-architecture/issues)
- 💬 [Discussions](https://github.com/panjidwisatrio/fastapi-clean-architecture/discussions)

---

<div align="center">

**Made with ❤️ using FastAPI and Clean Architecture principles**

⭐ Star this repo if you find it helpful!

</div>
