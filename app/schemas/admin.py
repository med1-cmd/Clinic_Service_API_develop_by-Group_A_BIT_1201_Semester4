from pydantic import BaseModel
from .base import NoIdCreateModel


class AdminCreate(NoIdCreateModel):
    full_name: str
    email: str
    password: str
    license_number: str


class UserPermissionSchema(BaseModel):
    permissions: list[str]


class MaintenanceModeSchema(BaseModel):
    enabled: bool
    message: str
