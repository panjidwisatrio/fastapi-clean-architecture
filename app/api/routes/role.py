from fastapi import APIRouter, Depends, Response, status
from typing import List, Union

from app.core.security import get_current_user_with_permission
from app.schemas.role import PermissionRole, Role, RoleCreate, RoleDetail, RoleSimple, RoleUpdate, UserAssignmentResult, UserUnassignmentResult, UsersRoleAssignment
from app.services.role_service import RoleService
from app.api.dependencies import (
    get_role_service,
    get_pagination_params,
)
from app.core.cache import cache_role
from app.core.config import settings

router = APIRouter(prefix="/roles", tags=["roles"])

@router.get("/default", response_model=RoleSimple)
async def get_default_role(
    service: RoleService = Depends(get_role_service),
    _: dict = Depends(get_current_user_with_permission("view_roles"))
):
    return service.get_default_role()

@router.patch("/default", response_model=RoleSimple)
async def set_default_role(
    role_id: int,
    service: RoleService = Depends(get_role_service),
    _: dict = Depends(get_current_user_with_permission("manage_roles"))
):
    return service.set_default_role(role_id)

@router.post("/", response_model=Role, status_code=status.HTTP_201_CREATED)
async def create_role(
    role: RoleCreate, 
    service: RoleService = Depends(get_role_service),
    _: dict = Depends(get_current_user_with_permission("manage_roles"))
):
    return await service.create_role(role)

@router.put("/{role_id}", response_model=Role)
async def update_role(
    role_id: int,
    role: RoleUpdate,
    service: RoleService = Depends(get_role_service),
    _: dict = Depends(get_current_user_with_permission("manage_roles"))
):
    return await service.update_role(role_id, role)

@router.get("/", response_model=List[RoleSimple])
@cache_role(expire=settings.CACHE_EXPIRE_SECONDS)
async def read_roles(
    response: Response,
    skip_limit: tuple = Depends(get_pagination_params), 
    service: RoleService = Depends(get_role_service),
    _: dict = Depends(get_current_user_with_permission("view_roles"))
):
    # Disable browser cache - force server revalidation
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    skip, limit = skip_limit
    return service.get_roles(skip, limit)

@router.get("/{role_id}", response_model=RoleDetail)
@cache_role(expire=settings.CACHE_EXPIRE_SECONDS)
async def read_role(
    response: Response,
    role_id: int, 
    service: RoleService = Depends(get_role_service),
    _: dict = Depends(get_current_user_with_permission("view_roles"))
):
    # Disable browser cache - force server revalidation
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return service.get_role(role_id)

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int, 
    service: RoleService = Depends(get_role_service),
    _: dict = Depends(get_current_user_with_permission("manage_roles"))
):
    await service.delete_role(role_id)
    return None

@router.post("/permissions", response_model=Role)
async def add_permission_to_role(
    permissions: PermissionRole,
    service: RoleService = Depends(get_role_service),
    _: dict = Depends(get_current_user_with_permission("manage_roles"))
):
    return service.add_permission_to_role(permissions)

@router.delete("/permissions", response_model=Role)
async def remove_permission_from_role(
    permissions: PermissionRole,
    service: RoleService = Depends(get_role_service),
    _: dict = Depends(get_current_user_with_permission("manage_roles"))
):
    return service.remove_permission_from_role(permissions)

@router.post("/assign/users", 
    description="Assign a role to multiple users. some time admin or manager want to assign role to multiple users at once.",
    response_model=Union[RoleDetail, UserAssignmentResult],
    responses={
        status.HTTP_207_MULTI_STATUS: {
            "description": "Partial Success - Some user assignments failed",
            "model": UserAssignmentResult,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Role not found",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {"type": "string"}
                        }
                    },
                    "example": {"detail": "Role not found"}
                }
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "All users failed to be assigned to role",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {
                                "oneOf": [
                                    {"type": "string"},
                                    {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "user_id": {"type": "integer"},
                                                "reason": {"type": "string"},
                                            },
                                            "required": ["user_id", "reason"],
                                        },
                                    },
                                ]
                            }
                        },
                        "required": ["detail"],
                    },
                    "examples": {
                        "string_error": {
                            "summary": "String error message",
                            "value": {"detail": "Some error occurred during assignment"}
                        },
                        "list_error": {
                            "summary": "List of failed assignments",
                            "value": {
                                "detail": [
                                    {"user_id": 1, "reason": "User not found"},
                                    {"user_id": 2, "reason": "User not active"}
                                ]
                            }
                        }
                    }
                }
            }
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Failed to assign users to role",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {"type": "string"}
                        }
                    },
                    "example": {"detail": "Failed to assign users to role"}
                }
            }
        }
    }
)
async def assign_role_to_user(
    assignment: UsersRoleAssignment,
    response: Response,
    service: RoleService = Depends(get_role_service),
    _: dict = Depends(get_current_user_with_permission("manage_roles"))
):
    result = service.assign_role_to_users(assignment)
    if isinstance(result, UserAssignmentResult) and result.failed_assignments:
        response.status_code = status.HTTP_207_MULTI_STATUS
    return result

@router.post("/unassign/users", 
    description="Unassign a role from multiple users. some time admin or manager want to unassign role from multiple users at once.",
    response_model=Union[RoleDetail, UserUnassignmentResult],
    responses={
        status.HTTP_207_MULTI_STATUS: {
            "description": "Partial Success - Some user unassignments failed",
            "model": UserUnassignmentResult,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Role not found",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {"type": "string"}
                        }
                    },
                    "example": {"detail": "Role not found"}
                }
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "All users failed to be assigned to role",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {
                                "oneOf": [
                                    {"type": "string"},
                                    {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "user_id": {"type": "integer"},
                                                "reason": {"type": "string"},
                                            },
                                            "required": ["user_id", "reason"],
                                        },
                                    },
                                ]
                            }
                        },
                        "required": ["detail"],
                    },
                    "examples": {
                        "string_error": {
                            "summary": "String error message",
                            "value": {"detail": "Some error occurred during unassignment"}
                        },
                        "list_error": {
                            "summary": "List of failed assignments",
                            "value": {
                                "detail": [
                                    {"user_id": 1, "reason": "User not found"},
                                    {"user_id": 2, "reason": "User not verified"}
                                ]
                            }
                        }
                    }
                }
            }
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Cannot unassign default role from users",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {"type": "string"}
                        }
                    },
                    "example": {"detail": "Cannot unassign default role from users"}
                }
            }
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Failed to unassign users from role",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "detail": {"type": "string"}
                        }
                    },
                    "example": {"detail": "Failed to unassign users from role"}
                }
            }
        }
    }
)
async def unassign_role_from_user(
    assignment: UsersRoleAssignment,
    response: Response,
    service: RoleService = Depends(get_role_service),
    _: dict = Depends(get_current_user_with_permission("manage_roles"))
):
    result = service.unassign_role_from_users(assignment)
    if isinstance(result, UserUnassignmentResult) and result.failed_unassignments:
        response.status_code = status.HTTP_207_MULTI_STATUS
    return result