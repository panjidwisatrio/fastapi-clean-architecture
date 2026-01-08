# Database Overview

Database architecture and schema design.

## Supported Databases

- PostgreSQL (recommended)
- MySQL
- SQLite (development only)

## Tables

- **users** - User accounts and authentication
- **roles** - User role definitions
- **permissions** - Granular access permissions
- **permission_role** - Many-to-many relationship
- **otp** - One-time passwords for verification
- **token_blacklist** - Invalidated JWT tokens

## Relationships

- User → Role (Many-to-One)
- Role ↔ Permission (Many-to-Many via permission_role)

## Design Principles

- Normalized schema
- Foreign key constraints
- Indexed columns for performance
- Timestamps for audit trail

See [Models](models.md) and [Migrations](migrations.md) for details.
