# Database Migrations

This guide covers everything you need to know about database migrations using Alembic in FastAPI Clean Architecture.

## Overview

**Alembic** is a lightweight database migration tool for SQLAlchemy. It allows you to:

- Track database schema changes in version control
- Generate migrations automatically from model changes
- Apply and rollback migrations safely
- Work with multiple environments (dev, test, prod)

!!! success "Already Configured"
    Alembic is already set up in this project. You don't need to run `alembic init`.

## Quick Start

!!! warning "Run Application First"
    Before creating migrations, run the application at least once to initialize the database:
    ```bash
    uvicorn app.main:app --reload
    ```
    This creates the database file and establishes the connection. Press `Ctrl+C` to stop after the app starts successfully.

```bash
# 1. Configure database URL in alembic.ini
# 2. Create initial migration
alembic revision --autogenerate -m "initial migration"

# 3. Apply migration
alembic upgrade head

# 4. Done! Your database is ready.
```

## Initial Setup

### Step 1: Configure Database URL

Edit `alembic.ini` and update the database URL (around line 90):

=== "SQLite (Development)"
    ```ini
    sqlalchemy.url = sqlite:///./test.db
    ```

=== "PostgreSQL"
    ```ini
    sqlalchemy.url = postgresql://user:password@localhost:5432/dbname
    ```

=== "MySQL"
    ```ini
    sqlalchemy.url = mysql://user:password@localhost:3306/dbname
    ```

!!! tip "Environment Variables"
    You can also configure this via environment variables in `alembic/env.py` to keep credentials separate from config files.

### Step 2: Create Initial Migration

!!! warning "Run Application First"
    Before creating migrations, run the application at least once to initialize the database:
    ```bash
    uvicorn app.main:app --reload
    ```
    This creates the database file and establishes the connection. Press `Ctrl+C` to stop after the app starts successfully.

After configuring your database models, create the initial migration:

```bash
alembic revision --autogenerate -m "initial migration"
```

This command will:

1. ✅ Scan your SQLAlchemy models in `app/models/`
2. ✅ Compare with current database state
3. ✅ Generate a migration script in `alembic/versions/`

Output example:

```
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'users'
INFO  [alembic.autogenerate.compare] Detected added table 'roles'
  Generating alembic/versions/abc123_initial_migration.py ...  done
```

### Step 3: Review Generated Migration

Check the generated migration file in `alembic/versions/`:

```python
# alembic/versions/abc123_initial_migration.py

def upgrade():
    """Create tables"""
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=True),
        sa.Column('first_name', sa.String(), nullable=True),
        sa.Column('last_name', sa.String(), nullable=True),
        sa.Column('role_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

def downgrade():
    """Drop tables"""
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
```

### Step 4: Apply Migration

Apply the migration to create database tables:

```bash
alembic upgrade head
```

Output:

```
INFO  [alembic.runtime.migration] Running upgrade  -> abc123, initial migration
```

🎉 Your database is now set up with all required tables!

## Common Commands

### Creating Migrations

#### Auto-generate Migration

When you modify your models, automatically generate a migration:

```bash
alembic revision --autogenerate -m "add phone_number to users"
```

#### Create Empty Migration

For complex changes or data migrations, create an empty migration:

```bash
alembic revision -m "migrate user data"
```

Then edit the generated file manually.

### Applying Migrations

```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade to specific version
alembic upgrade abc123

# Upgrade one version forward
alembic upgrade +1

# Upgrade two versions forward
alembic upgrade +2
```

### Rolling Back Migrations

```bash
# Downgrade to previous version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade abc123

# Downgrade all migrations
alembic downgrade base
```

!!! danger "Production Rollbacks"
    Test rollbacks in development first. Some changes (like dropping columns) may result in data loss.

### Viewing History

```bash
# Show current version
alembic current

# Show migration history
alembic history

# Show verbose history
alembic history --verbose

# Show pending migrations
alembic heads
```

## Migration Workflow

Here's the typical workflow for different scenarios:

### Scenario 1: Adding a New Field to Existing Table

#### 1. Modify Your Model

```python
# app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String(20), nullable=True)  # ← New field
    is_active = Column(Boolean, default=True)
```

#### 2. Generate Migration

```bash
alembic revision --autogenerate -m "add phone_number to users"
```

#### 3. Review Migration

Open `alembic/versions/xyz789_add_phone_number_to_users.py`:

```python
def upgrade():
    op.add_column('users', sa.Column('phone_number', sa.String(length=20), nullable=True))

def downgrade():
    op.drop_column('users', 'phone_number')
```

#### 4. Apply Migration

```bash
alembic upgrade head
```

#### 5. Test

Verify the changes work correctly in your application.

#### 6. Commit

```bash
git add app/models/user.py alembic/versions/xyz789_add_phone_number_to_users.py
git commit -m "Add phone_number field to User model"
```

---

### Scenario 2: Adding a New Table

#### 1. Create New Model File

```python
# app/models/product.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Product(Base):
    """Product model for e-commerce."""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(String(1000), nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("Category", back_populates="products")
```

#### 2. Register Model in `__init__.py`

```python
# app/models/__init__.py
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.product import Product  # ← Add new model
```

#### 3. Import Model in Alembic env.py

Ensure the model is imported so Alembic can detect it:

```python
# alembic/env.py
from app.models import user, role, permission, product  # ← Add product
```

#### 4. Generate Migration

```bash
alembic revision --autogenerate -m "add products table"
```

#### 5. Review Generated Migration

Open `alembic/versions/abc456_add_products_table.py`:

```python
def upgrade():
    # Create products table
    op.create_table('products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('stock', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False)
    op.create_index(op.f('ix_products_name'), 'products', ['name'], unique=False)

def downgrade():
    # Drop products table
    op.drop_index(op.f('ix_products_name'), table_name='products')
    op.drop_index(op.f('ix_products_id'), table_name='products')
    op.drop_table('products')
```

#### 6. Apply Migration

```bash
alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade xyz789 -> abc456, add products table
```

#### 7. Verify Table Creation

```bash
# Check current version
alembic current

# Or connect to database and verify
# For SQLite:
sqlite3 test.db ".schema products"
```

#### 8. Create Repository (Optional)

```python
# app/repositories/product_repository.py
from sqlalchemy.orm import Session
from app.models.product import Product
from typing import Optional, List

class ProductRepository:
    """Repository for Product operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, product_data: dict) -> Product:
        """Create new product."""
        product = Product(**product_data)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product
    
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID."""
        return self.db.query(Product).filter(Product.id == product_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """Get all products."""
        return self.db.query(Product).offset(skip).limit(limit).all()
```

#### 9. Create Service (Optional)

```python
# app/services/product_service.py
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate
from fastapi import HTTPException

class ProductService:
    """Service for Product business logic."""
    
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository
    
    def create_product(self, product_data: ProductCreate):
        """Create new product with validation."""
        # Business logic
        if product_data.price <= 0:
            raise HTTPException(status_code=400, detail="Price must be positive")
        
        return self.product_repository.create(product_data.dict())
```

#### 10. Commit Changes

```bash
git add app/models/product.py \
        app/models/__init__.py \
        app/repositories/product_repository.py \
        app/services/product_service.py \
        alembic/versions/abc456_add_products_table.py
        
git commit -m "Add Product model with repository and service"
```

---

### Scenario 3: Adding Multiple Related Tables

When adding tables with relationships:

#### 1. Create All Models

```python
# app/models/category.py
class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    products = relationship("Product", back_populates="category")

# app/models/product.py (with relationship)
class Product(Base):
    __tablename__ = "products"
    # ... fields ...
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="products")
```

#### 2. Generate Single Migration

```bash
alembic revision --autogenerate -m "add categories and products tables"
```

!!! tip "Single Migration for Related Tables"
    It's better to create related tables in a single migration to maintain referential integrity.

#### 3. Review & Apply

```bash
# Review the migration file
# Apply migration
alembic upgrade head
```

---

### Quick Comparison

| Scenario | Command | Files to Modify |
|----------|---------|-----------------|
| **Add Field** | `alembic revision --autogenerate -m "add field"` | 1 model file |
| **Add Table** | `alembic revision --autogenerate -m "add table"` | 1 model file + `__init__.py` |
| **Add Multiple Tables** | `alembic revision --autogenerate -m "add tables"` | Multiple model files + `__init__.py` |

---

## Multiple Environments

### Using Environment Variables

Modify `alembic/env.py` to use environment-specific database URLs:

```python
# alembic/env.py
import os
from app.core.config import get_settings

config = context.config
settings = get_settings()

# Override alembic.ini with environment-specific URL
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)
```

Now you can use different databases per environment:

```bash
# Development
export ENVIRONMENT=development
alembic upgrade head

# Production
export ENVIRONMENT=production
alembic upgrade head
```

## Advanced Topics

### Manual Migrations

For complex changes, create and edit migrations manually:

```bash
alembic revision -m "complex data migration"
```

Edit the generated file:

```python
def upgrade():
    # Custom SQL or Python code
    op.execute("""
        UPDATE users 
        SET email = LOWER(email)
        WHERE email != LOWER(email)
    """)

def downgrade():
    # Revert logic
    pass
```

### Branching and Merging

If multiple developers create migrations, you may need to merge:

```bash
# Check for multiple heads
alembic heads

# Merge branches
alembic merge -m "merge migrations" head1 head2
```

### Offline Migrations

Generate SQL for offline execution:

```bash
# Generate SQL for upgrade
alembic upgrade head --sql > migration.sql

# Generate SQL for downgrade
alembic downgrade -1 --sql > rollback.sql
```

## Troubleshooting

### "No changes detected" When Models Changed

**Causes:**

- Models not imported in `alembic/env.py`
- Alembic can't detect certain changes (e.g., column type changes)
- Database already has the changes

**Solution:**

1. Ensure all models are imported in `alembic/env.py`:
   ```python
   from app.models import user, role, permission, otp, token_blacklist
   ```

2. For unsupported changes, create manual migration:
   ```bash
   alembic revision -m "manual change"
   ```

### Migration Conflicts

**Problem:** Multiple heads or conflicts

**Solution:**

```bash
# Check current state
alembic current
alembic heads

# Merge if needed
alembic merge -m "merge conflicts" head1 head2
```

### Database Out of Sync

**Problem:** Database state doesn't match migrations

**Solution:**

```bash
# Mark database as current without running migrations
alembic stamp head

# Or in development, start fresh:
# 1. Delete database file (SQLite) or drop tables
# 2. Run: alembic upgrade head
```

### Can't Rollback Migration

**Problem:** Downgrade fails

**Solution:**

- Review the downgrade function in the migration file
- Ensure downgrade logic is correct
- Test downgrades in development first
- Some changes may not be reversible (data loss)

## Best Practices

✅ **DO:**

- Always review auto-generated migrations
- Test migrations on development database first
- Backup production database before migrating
- Commit migrations with related code changes
- Use descriptive migration messages
- Test both upgrade and downgrade paths
- Keep migrations small and focused

❌ **DON'T:**

- Never edit applied migrations
- Don't skip reviewing auto-generated code
- Don't apply untested migrations to production
- Don't commit without testing migrations locally

## Production Checklist

Before applying migrations to production:

- [ ] Test migration on development database
- [ ] Test migration on staging database (if available)
- [ ] Review migration script thoroughly
- [ ] Backup production database
- [ ] Plan rollback strategy
- [ ] Schedule maintenance window (if needed)
- [ ] Prepare rollback script
- [ ] Apply migration: `alembic upgrade head`
- [ ] Verify migration: `alembic current`
- [ ] Test application functionality
- [ ] Monitor for errors

## Quick Reference

For quick command reference, see `alembic/README` in the project:

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Create new migration after changes
alembic revision --autogenerate -m "new changes"
alembic upgrade head
```

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Auto Generating Migrations](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)

## What's Next?

After setting up migrations:

- [Models](models.md) - Learn about database models
- [Seeding](seeding.md) - Initialize database with data
- [First Steps](../getting-started/first-steps.md) - Start using the API
