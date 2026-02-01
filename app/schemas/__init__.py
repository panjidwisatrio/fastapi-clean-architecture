# Avoid circular imports by using import statements here

# Import all schemas
from app.schemas.user import *
from app.schemas.role import *
from app.schemas.permission import *

# Update forward references after all imports
from app.schemas.user import update_schemas as update_user_schemas
from app.schemas.role import update_schemas as update_role_schemas

update_user_schemas()
update_role_schemas()