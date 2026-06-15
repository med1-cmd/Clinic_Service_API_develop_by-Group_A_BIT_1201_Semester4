from datetime import date
from pydantic import BaseModel
from .base import NoIdCreateModel, NoIdUpdateModel


class UserCreate(NoIdCreateModel):
    full_name: str
    email: str
    password: str
    role: str


class PatientCreate(NoIdCreateModel):
    full_name: str
    email: str
    password: str
    phone: str
    date_of_birth: date
    gender: str


class UserUpdate(BaseModel):
    model_config = {
        "extra": "forbid"
    }

    id: int | None = None
    full_name: str | None = None
    email: str | None = None
    role: str | None = None
    phone: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    specialty: str | None = None
    years_experience: int | None = None
    license_number: str | None = None
    clinic_id: int | None = None


class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    phone: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    specialty: str | None = None
    years_experience: int | None = None
    license_number: str | None = None
    clinic_id: int | None = None

    class Config:
        from_attributes = True


class PatientUpdate(NoIdUpdateModel):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None


class PatientOut(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    phone: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None

    class Config:
        from_attributes = True


class LoginSchema(BaseModel):
    email: str
    password: str
