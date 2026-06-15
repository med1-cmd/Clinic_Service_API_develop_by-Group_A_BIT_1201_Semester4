from pydantic import BaseModel
from datetime import datetime
from .base import NoIdCreateModel


class NotificationCreate(NoIdCreateModel):
    recipient_id: int
    title: str
    message: str


class NotificationOut(BaseModel):
    id: int
    recipient_id: int
    sender_id: int
    title: str
    message: str
    is_read: int
    created_at: datetime

    class Config:
        from_attributes = True


class HealthCheckResponse(BaseModel):
    status: str
    service: str
    async_enabled: bool


class PrescriptionAlertOut(BaseModel):
    prescription_id: int
    patient_id: int
    doctor_id: int
    medication: str
    dosage: str
    instructions: str
    created_at: datetime
    alert_type: str


class PrescriptionAlertList(BaseModel):
    total_alerts: int
    alerts: list[PrescriptionAlertOut]


class AcknowledgePrescriptionResponse(BaseModel):
    message: str
    prescription_id: int
