#!/usr/bin/env python3
"""
CLI tool for generating FastAPI boilerplate code.
Usage: python generate.py <command> <name> [options]

Commands:
  model       Generate a new model
  schema      Generate Pydantic schemas
  repository  Generate repository
  service     Generate service
  route       Generate API routes
  crud        Generate complete CRUD (all of the above)

Examples:
  python generate.py model Product
  python generate.py crud Product
  python generate.py crud Product --fields "name:str,price:float,description:str"
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict
import inflect

p = inflect.engine()


class CodeGenerator:
    def __init__(self, name: str, fields: List[Dict] = None):
        self.name = name
        self.snake_name = self._to_snake_case(name)
        self.plural_name = p.plural(self.snake_name)
        self.fields = fields or []
        
    def _to_snake_case(self, name: str) -> str:
        """Convert PascalCase to snake_case"""
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
    
    def _parse_fields(self, fields_str: str) -> List[Dict]:
        """Parse fields string like 'name:str,price:float,description:str'"""
        if not fields_str:
            return []
        
        fields = []
        for field in fields_str.split(','):
            field_name, field_type = field.strip().split(':')
            fields.append({
                'name': field_name.strip(),
                'type': field_type.strip(),
                'python_type': self._get_python_type(field_type.strip())
            })
        return fields
    
    def _get_python_type(self, field_type: str) -> str:
        """Convert field type to Python type"""
        type_mapping = {
            'str': 'String',
            'string': 'String',
            'int': 'Integer',
            'integer': 'Integer',
            'float': 'Float',
            'bool': 'Boolean',
            'boolean': 'Boolean',
            'datetime': 'DateTime',
            'date': 'Date',
            'text': 'Text',
        }
        return type_mapping.get(field_type.lower(), 'String')
    
    def generate_model(self) -> str:
        """Generate SQLAlchemy model"""
        fields_code = "\n    ".join([
            f'{field["name"]} = Column({field["python_type"]})'
            for field in self.fields
        ])
        
        if not fields_code:
            fields_code = '# Add your fields here\n    # example: name = Column(String)'
        
        return f'''# filepath: app/models/{self.snake_name}.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class {self.name}(Base):
    __tablename__ = "{self.plural_name}"

    id = Column(Integer, primary_key=True, index=True)
    {fields_code}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Add relationships here if needed
    # example: user = relationship("User", back_populates="{self.plural_name}")
'''

    def generate_schemas(self) -> str:
        """Generate Pydantic schemas"""
        fields_code = "\n    ".join([
            f'{field["name"]}: {field["type"]}'
            for field in self.fields
        ])
        
        if not fields_code:
            fields_code = '# Add your fields here\n    # example: name: str'
        
        return f'''# filepath: app/schemas/{self.snake_name}.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class {self.name}Base(BaseModel):
    {fields_code}


class {self.name}Create({self.name}Base):
    pass


class {self.name}Update(BaseModel):
    """All fields are optional for update"""
    {chr(10).join([f"    {field['name']}: Optional[{field['type']}] = None" for field in self.fields])}


class {self.name}InDB({self.name}Base):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class {self.name}({self.name}InDB):
    pass
'''

    def generate_repository(self) -> str:
        """Generate repository"""
        return f'''# filepath: app/repositories/{self.snake_name}_repository.py
from typing import Optional, List
from sqlalchemy.orm import Session
from app.core.logging import setup_logger, log_operation
from app.models.{self.snake_name} import {self.name}
from app.schemas.{self.snake_name} import {self.name}Create, {self.name}Update

logger = setup_logger("{self.snake_name}_repositories")


class {self.name}Repository:
    def __init__(self, db: Session):
        self.db = db
    
    @log_operation(logger)
    def get_{self.snake_name}(self, {self.snake_name}_id: int) -> Optional[{self.name}]:
        """Get {self.snake_name} by ID"""
        return self.db.query({self.name}).filter({self.name}.id == {self.snake_name}_id).first()

    @log_operation(logger)
    def get_{self.plural_name}(self, skip: int = 0, limit: int = 100) -> List[{self.name}]:
        """Get all {self.plural_name} with pagination"""
        return self.db.query({self.name}).offset(skip).limit(limit).all()

    @log_operation(logger)
    def create_{self.snake_name}(self, {self.snake_name}: {self.name}Create) -> {self.name}:
        """Create new {self.snake_name}"""
        db_{self.snake_name} = {self.name}(**{self.snake_name}.dict())
        self.db.add(db_{self.snake_name})
        self.db.commit()
        self.db.refresh(db_{self.snake_name})
        return db_{self.snake_name}

    @log_operation(logger)
    def update_{self.snake_name}(self, {self.snake_name}_id: int, {self.snake_name}: {self.name}Update) -> Optional[{self.name}]:
        """Update {self.snake_name}"""
        db_{self.snake_name} = self.get_{self.snake_name}({self.snake_name}_id)
        if db_{self.snake_name}:
            update_data = {self.snake_name}.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_{self.snake_name}, field, value)
            self.db.commit()
            self.db.refresh(db_{self.snake_name})
        return db_{self.snake_name}

    @log_operation(logger)
    def delete_{self.snake_name}(self, {self.snake_name}_id: int) -> Optional[{self.name}]:
        """Delete {self.snake_name}"""
        db_{self.snake_name} = self.get_{self.snake_name}({self.snake_name}_id)
        if db_{self.snake_name}:
            self.db.delete(db_{self.snake_name})
            self.db.commit()
        return db_{self.snake_name}
'''

    def generate_service(self) -> str:
        """Generate service"""
        return f'''# filepath: app/services/{self.snake_name}_service.py
from typing import List
from fastapi import HTTPException, status
from app.core.logging import setup_logger, log_operation
from app.repositories.{self.snake_name}_repository import {self.name}Repository
from app.schemas.{self.snake_name} import {self.name}, {self.name}Create, {self.name}Update

logger = setup_logger("{self.snake_name}_services")


class {self.name}Service:
    def __init__(self, {self.snake_name}_repository: {self.name}Repository):
        self.{self.snake_name}_repository = {self.snake_name}_repository

    @log_operation(logger)
    def create_{self.snake_name}(self, {self.snake_name}: {self.name}Create) -> {self.name}:
        """
        Create a new {self.snake_name}
        
        Business Logic:
        1. Validate input data
        2. Check for duplicates if needed
        3. Create {self.snake_name} in database
        
        Args:
            {self.snake_name} ({self.name}Create): {self.name} creation data
            
        Returns:
            {self.name}: Created {self.snake_name} object
            
        Raises:
            HTTPException: Validation errors
        """
        # Add business logic here
        # Example: Check if {self.snake_name} already exists
        # existing = self.{self.snake_name}_repository.get_{self.snake_name}_by_field(...)
        # if existing:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="{self.name} already exists"
        #     )
        
        return self.{self.snake_name}_repository.create_{self.snake_name}({self.snake_name})

    @log_operation(logger)
    def get_{self.snake_name}(self, {self.snake_name}_id: int) -> {self.name}:
        """Get {self.snake_name} by ID"""
        {self.snake_name} = self.{self.snake_name}_repository.get_{self.snake_name}({self.snake_name}_id)
        if not {self.snake_name}:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="{self.name} not found"
            )
        return {self.snake_name}

    @log_operation(logger)
    def get_{self.plural_name}(self, skip: int = 0, limit: int = 100) -> List[{self.name}]:
        """Get all {self.plural_name}"""
        return self.{self.snake_name}_repository.get_{self.plural_name}(skip, limit)

    @log_operation(logger)
    def update_{self.snake_name}(self, {self.snake_name}_id: int, {self.snake_name}: {self.name}Update) -> {self.name}:
        """Update {self.snake_name}"""
        db_{self.snake_name} = self.{self.snake_name}_repository.update_{self.snake_name}({self.snake_name}_id, {self.snake_name})
        if not db_{self.snake_name}:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="{self.name} not found"
            )
        return db_{self.snake_name}

    @log_operation(logger)
    def delete_{self.snake_name}(self, {self.snake_name}_id: int) -> {self.name}:
        """Delete {self.snake_name}"""
        db_{self.snake_name} = self.{self.snake_name}_repository.delete_{self.snake_name}({self.snake_name}_id)
        if not db_{self.snake_name}:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="{self.name} not found"
            )
        return db_{self.snake_name}
'''

    def generate_routes(self) -> str:
        """Generate API routes"""
        return f'''# filepath: app/api/routes/{self.snake_name}.py
from fastapi import APIRouter, Depends, status
from typing import List

from app.schemas.{self.snake_name} import {self.name}, {self.name}Create, {self.name}Update
from app.services.{self.snake_name}_service import {self.name}Service
from app.api.dependencies import (
    get_{self.snake_name}_service,
    get_pagination_params,
    get_current_user_with_permission
)

router = APIRouter(prefix="/{self.plural_name}", tags=["{self.plural_name}"])


@router.post("/", response_model={self.name}, status_code=status.HTTP_201_CREATED)
async def create_{self.snake_name}(
    {self.snake_name}: {self.name}Create, 
    service: {self.name}Service = Depends(get_{self.snake_name}_service),
    _: dict = Depends(get_current_user_with_permission("create_{self.snake_name}"))
):
    """Create a new {self.snake_name}"""
    return service.create_{self.snake_name}({self.snake_name})


@router.get("/", response_model=List[{self.name}])
async def read_{self.plural_name}(
    skip_limit: tuple = Depends(get_pagination_params), 
    service: {self.name}Service = Depends(get_{self.snake_name}_service),
    _: dict = Depends(get_current_user_with_permission("read_{self.plural_name}"))
):
    """Get all {self.plural_name}"""
    skip, limit = skip_limit
    return service.get_{self.plural_name}(skip, limit)


@router.get("/{{{{id}}}}", response_model={self.name})
async def read_{self.snake_name}(
    id: int, 
    service: {self.name}Service = Depends(get_{self.snake_name}_service),
    _: dict = Depends(get_current_user_with_permission("read_{self.snake_name}"))
):
    """Get {self.snake_name} by ID"""
    return service.get_{self.snake_name}(id)


@router.put("/{{{{id}}}}", response_model={self.name})
async def update_{self.snake_name}(
    id: int,
    {self.snake_name}: {self.name}Update,
    service: {self.name}Service = Depends(get_{self.snake_name}_service),
    _: dict = Depends(get_current_user_with_permission("update_{self.snake_name}"))
):
    """Update {self.snake_name}"""
    return service.update_{self.snake_name}(id, {self.snake_name})


@router.delete("/{{{{id}}}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{self.snake_name}(
    id: int, 
    service: {self.name}Service = Depends(get_{self.snake_name}_service),
    _: dict = Depends(get_current_user_with_permission("delete_{self.snake_name}"))
):
    """Delete {self.snake_name}"""
    service.delete_{self.snake_name}(id)
    return None
'''

    def generate_dependency(self) -> str:
        """Generate dependency injection code"""
        return f'''
# Add this to app/api/dependencies.py

def get_{self.snake_name}_service(db: Session = Depends(get_db)) -> {self.name}Service:
    """Returns a {self.name}Service instance with its required repository"""
    return {self.name}Service({self.name}Repository(db))
'''

    def generate_main_import(self) -> str:
        """Generate import statement for main.py"""
        return f'''
# Add this to app/main.py

from app.api.routes import {self.snake_name}

# ... (inside your FastAPI app initialization)
app.include_router({self.snake_name}.router)
'''

    def write_file(self, path: str, content: str):
        """Write content to file"""
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Generated: {path}")


def main():
    parser = argparse.ArgumentParser(
        description="FastAPI Code Generator - Generate boilerplate code for FastAPI applications"
    )
    
    parser.add_argument(
        'command',
        choices=['model', 'schema', 'repository', 'service', 'route', 'crud', 'dependency'],
        help='Type of code to generate'
    )
    
    parser.add_argument(
        'name',
        help='Name of the entity (e.g., Product, User, Order)'
    )
    
    parser.add_argument(
        '--fields',
        type=str,
        help='Fields definition (e.g., "name:str,price:float,description:text")',
        default=''
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing files'
    )
    
    args = parser.parse_args()
    
    # Parse fields if provided
    generator = CodeGenerator(args.name)
    if args.fields:
        generator.fields = generator._parse_fields(args.fields)
    
    print(f"\n🚀 Generating {args.command} for {args.name}...\n")
    
    # Generate based on command
    if args.command == 'model' or args.command == 'crud':
        generator.write_file(
            f'app/models/{generator.snake_name}.py',
            generator.generate_model()
        )
    
    if args.command == 'schema' or args.command == 'crud':
        generator.write_file(
            f'app/schemas/{generator.snake_name}.py',
            generator.generate_schemas()
        )
    
    if args.command == 'repository' or args.command == 'crud':
        generator.write_file(
            f'app/repositories/{generator.snake_name}_repository.py',
            generator.generate_repository()
        )
    
    if args.command == 'service' or args.command == 'crud':
        generator.write_file(
            f'app/services/{generator.snake_name}_service.py',
            generator.generate_service()
        )
    
    if args.command == 'route' or args.command == 'crud':
        generator.write_file(
            f'app/api/routes/{generator.snake_name}.py',
            generator.generate_routes()
        )
    
    if args.command == 'dependency' or args.command == 'crud':
        print("\n📝 Manual steps required:")
        print(generator.generate_dependency())
        print(generator.generate_main_import())
    
    print(f"\n✅ Code generation completed!")
    print(f"\n📚 Next steps:")
    print(f"1. Review generated files")
    print(f"2. Add the dependency to app/api/dependencies.py")
    print(f"3. Import and register the router in app/main.py")
    print(f"4. Run database migrations if needed")
    print(f"5. Add permissions to app/data/permissions.json:")
    print(f'   - create_{generator.snake_name}')
    print(f'   - read_{generator.plural_name}')
    print(f'   - read_{generator.snake_name}')
    print(f'   - update_{generator.snake_name}')
    print(f'   - delete_{generator.snake_name}')


if __name__ == '__main__':
    main()