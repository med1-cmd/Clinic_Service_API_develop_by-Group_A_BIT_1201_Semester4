import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Prescription, User, Notification
from app.schemas import (
    NotificationCreate,
    NotificationOut,
    HealthCheckResponse,
    PrescriptionAlertOut,
    PrescriptionAlertList,
    AcknowledgePrescriptionResponse,
)
from app.deps import get_current_user
from app.constants import Roles

router = APIRouter(prefix="/notifications", tags=["Notifications"])


# 📢 Authenticated: Send a notification asynchronously.
@router.post(
    "/send-async",
    status_code=201,
    response_model=NotificationOut,
    summary="Authenticated: Send a notification asynchronously"
)
async def send_notification_async(
    data: NotificationCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Send a notification asynchronously and persist it.
    """
    recipient = db.query(User).filter(User.id == data.recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")

    notification = Notification(
        recipient_id=data.recipient_id,
        sender_id=user["id"],
        title=data.title,
        message=data.message
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    await asyncio.sleep(1)
    return notification


# ⚡ Public: Run the async health check endpoint.
@router.get(
    "/health-check",
    response_model=HealthCheckResponse,
    summary="Public: Run the async health check endpoint"
)
async def health_check_async():
    """
    Run a lightweight async health check.
    """
    await asyncio.sleep(0.5)
    return HealthCheckResponse(
        status="healthy",
        service="clinic-api",
        async_enabled=True
    )


# 📋 Authenticated: Get prescription alerts.
@router.get(
    "/prescription-alerts",
    response_model=PrescriptionAlertList,
    summary="Authenticated: Get prescription alerts"
)
async def get_prescription_alerts(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Return prescription alerts for the authenticated user.
    """
    if user["role"] == Roles.PATIENT:
        prescriptions = db.query(Prescription).filter(
            Prescription.patient_id == user["id"]
        ).all()
    elif user["role"] == Roles.DOCTOR:
        prescriptions = db.query(Prescription).filter(
            Prescription.doctor_id == user["id"]
        ).all()
    else:
        prescriptions = []

    alerts = [
        PrescriptionAlertOut(
            prescription_id=p.id,
            patient_id=p.patient_id,
            doctor_id=p.doctor_id,
            medication=p.medication,
            dosage=p.dosage,
            instructions=p.instructions,
            created_at=p.created_at,
            alert_type="new_prescription"
        )
        for p in prescriptions
    ]

    return PrescriptionAlertList(total_alerts=len(alerts), alerts=alerts)


# 📌 Authenticated: Acknowledge prescription alert.
@router.post(
    "/prescription-alerts/acknowledge/{prescription_id}",
    response_model=AcknowledgePrescriptionResponse,
    summary="Authenticated: Acknowledge prescription alert"
)
async def acknowledge_prescription_alert(
    prescription_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Acknowledge or mark a prescription alert as read.
    """
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    if prescription.patient_id != user["id"] and prescription.doctor_id != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied to this prescription")

    return AcknowledgePrescriptionResponse(
        message="Prescription alert acknowledged",
        prescription_id=prescription_id
    )
