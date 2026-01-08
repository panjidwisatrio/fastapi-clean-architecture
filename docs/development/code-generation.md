# Code Generation CLI

Automated module generator for rapid development.

## Overview

The code generation tool creates complete CRUD modules with all necessary files following clean architecture principles.

## Usage

```bash
python module/generate.py <module_name>
```

## Generated Files

For module `product`, the generator creates:

```
app/
├── models/product.py           # Database model
├── schemas/product.py          # Pydantic schemas
├── repositories/product_repository.py  # Data access
├── services/product_service.py         # Business logic
└── api/routes/product.py              # API endpoints
```

## Example

```bash
python module/generate.py product
```

Creates a complete product management module with:
- CRUD operations
- Proper dependency injection
- Input validation
- Error handling

## Customization

Edit templates in `module/` directory to customize generated code.

## Benefits

- Consistent code structure
- Reduces boilerplate
- Follows project patterns
- Saves development time

See implementation in `module/generate.py`.
