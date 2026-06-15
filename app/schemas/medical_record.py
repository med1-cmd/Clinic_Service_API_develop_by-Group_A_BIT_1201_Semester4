from pydantic import BaseModel
from .base import NoIdCreateModel, NoIdUpdateModel
from datetime import datetime


class MedicalRecordCreate(NoIdCreateModel):
    patient_id: int
    doctor_id: int
    diagnosis: str
    treatment: str
    notes: str


class MedicalRecordUpdate(NoIdUpdateModel):
    diagnosis: str | None = None
    treatment: str | None = None
    notes: str | None = None


class MedicalRecordOut(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    diagnosis: str
    treatment: str
    notes: str
    created_at: datetime

    class Config:
        from_attributes = True
