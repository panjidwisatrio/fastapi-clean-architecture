# Changelog

All notable changes to this project will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- WebSocket support for real-time features
- Two-factor authentication
- Rate limiting middleware
- API versioning system
- Background task queue
- File upload handling

## [1.0.0] - 2024-01-15

### Added
- Initial release of FastAPI Clean Architecture
- User authentication with JWT tokens
- Role-based access control (RBAC)
- Permission system
- Password reset with OTP
- Email service integration
- Database migrations with Alembic
- SQLAlchemy models (User, Role, Permission, OTP, TokenBlacklist)
- Repository pattern implementation
- Service layer for business logic
- RESTful API endpoints
- Interactive API documentation (Swagger UI)
- Pydantic schemas for validation
- Logging system
- Environment-based configuration
- Code generation CLI tool
- Database seeding with initial data
- Comprehensive test structure
- Clean Architecture layers
- Dependency injection
- Docker support
- Production deployment guide
- Complete documentation with MkDocs

### API Endpoints

#### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/forgot-password` - Request password reset
- `POST /api/v1/auth/reset-password` - Reset password with OTP

#### Users
- `GET /api/v1/users` - List users (admin only)
- `POST /api/v1/users` - Create user (admin only)
- `GET /api/v1/users/{user_id}` - Get user details
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user
- `GET /api/v1/me` - Get current user
- `PUT /api/v1/me` - Update current user
- `PUT /api/v1/me/password` - Change password

#### Roles
- `GET /api/v1/roles` - List roles
- `POST /api/v1/roles` - Create role (admin only)
- `GET /api/v1/roles/{role_id}` - Get role details
- `PUT /api/v1/roles/{role_id}` - Update role
- `DELETE /api/v1/roles/{role_id}` - Delete role

#### Permissions
- `GET /api/v1/permissions` - List permissions
- `POST /api/v1/permissions` - Create permission (admin only)
- `GET /api/v1/permissions/{permission_id}` - Get permission details
- `PUT /api/v1/permissions/{permission_id}` - Update permission
- `DELETE /api/v1/permissions/{permission_id}` - Delete permission

#### OTP
- `POST /api/v1/otp/request` - Request OTP
- `POST /api/v1/otp/verify` - Verify OTP

### Database Schema
- Users table with authentication fields
- Roles table for user roles
- Permissions table for granular access control
- Permission-Role association table (many-to-many)
- OTP table for one-time passwords
- Token blacklist for logout functionality

### Security Features
- Password hashing with bcrypt
- JWT token generation and validation
- Token blacklisting for logout
- Permission-based authorization
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy ORM
- Environment variable configuration

### Developer Tools
- Module generator CLI (`python -m module.generate`)
- Database migration commands
- Interactive API documentation
- Development environment setup
- VS Code debug configuration
- Logging to file and console

### Documentation
- Complete MkDocs documentation site
- Architecture overview and principles
- API endpoint documentation
- Database schema documentation
- Development guides
- Deployment guides (Production, Docker, Cloud)
- Troubleshooting guides
- Contributing guidelines

## [0.1.0] - 2023-12-01

### Added
- Project structure setup
- Basic FastAPI application
- SQLAlchemy integration
- User model and authentication
- Initial API endpoints

---

## Version History

- **v1.0.0** (2024-01-15) - First stable release
- **v0.1.0** (2023-12-01) - Initial prototype

## Release Notes

### v1.0.0 Highlights

This release provides a production-ready FastAPI boilerplate with Clean Architecture principles. Key features include:

- **Complete Authentication System**: Registration, login, logout, password reset
- **Authorization**: Role-based access control with granular permissions
- **Clean Architecture**: Well-organized layers for maintainability
- **Developer Experience**: CLI tools, documentation, examples
- **Production Ready**: Docker, deployment guides, logging, error handling

### Breaking Changes

None - this is the initial release.

### Migration Guide

Not applicable - initial release.

## Upcoming Releases

See [Roadmap](roadmap.md) for planned features in future versions.

## Support

- Report bugs via [GitHub Issues](https://github.com/panjidwisatrio/fastapi-clean-architecture/issues)
- Feature requests via [GitHub Discussions](https://github.com/panjidwisatrio/fastapi-clean-architecture/discussions)
- Security issues: Report privately to maintainers

## Contributors

Thank you to all contributors who helped build this project!

- See [GitHub Contributors](https://github.com/panjidwisatrio/fastapi-clean-architecture/graphs/contributors)
- See [Contributing Guidelines](../contributing/guidelines.md) to join us
