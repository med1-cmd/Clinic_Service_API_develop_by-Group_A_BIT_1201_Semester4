from pydantic import BaseModel
from .base import NoIdCreateModel, NoIdUpdateModel


class ClinicCreate(NoIdCreateModel):
    name: str
    address: str
    phone: str
    email: str
    specialty: str
    description: str | None = None


class ClinicUpdate(NoIdUpdateModel):
    name: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    specialty: str | None = None
    description: str | None = None


class ClinicOut(ClinicCreate):
    id: int

    class Config:
        from_attributes = True
