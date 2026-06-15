from pydantic import BaseModel
from .base import NoIdCreateModel, NoIdUpdateModel


class ServiceCreate(NoIdCreateModel):
    clinic_id: int
    service_name: str
    description: str | None = None


class ServiceUpdate(NoIdUpdateModel):
    clinic_id: int | None = None
    service_name: str | None = None
    description: str | None = None


class ServiceOut(ServiceCreate):
    id: int

    class Config:
        from_attributes = True
