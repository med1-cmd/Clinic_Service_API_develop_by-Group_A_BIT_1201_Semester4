from pydantic import BaseModel
from .base import NoIdCreateModel, NoIdUpdateModel


class PrescriptionCreate(NoIdCreateModel):
    patient_id: int
    doctor_id: int
    medication: str
    dosage: str
    frequency: str
    duration: str
    instructions: str


class PrescriptionUpdate(NoIdUpdateModel):
    medication: str | None = None
    dosage: str | None = None
    frequency: str | None = None
    duration: str | None = None
    instructions: str | None = None


class PrescriptionOut(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    medication: str
    dosage: str
    frequency: str
    duration: str
    instructions: str

    class Config:
        from_attributes = True
