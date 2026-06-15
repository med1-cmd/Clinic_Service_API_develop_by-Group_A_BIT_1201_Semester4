from datetime import date
from pydantic import BaseModel
from .base import NoIdCreateModel


class AppointmentCreate(NoIdCreateModel):
    doctor_id: int
    clinic_id: int
    appointment_date: date
    appointment_time: str
    reason: str


class AppointmentReschedule(BaseModel):
    appointment_date: date
    appointment_time: str


class AppointmentOut(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    clinic_id: int
    reason: str
    status: str
    appointment_date: date
    appointment_time: str

    class Config:
        from_attributes = True
