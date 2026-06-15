from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Appointment, Clinic, User
from app.schemas.appointment import AppointmentCreate, AppointmentOut, AppointmentReschedule
from app.deps import get_current_user, require_admin, require_doctor, require_patient
from app.constants import Roles

router = APIRouter(prefix="/appointments", tags=["Appointments"])


def _serialize_appointment(appointment):
    ad = getattr(appointment, "appointment_date", None)
    if isinstance(ad, datetime):
        appointment_date = ad.date()
    else:
        appointment_date = ad
    return {
        "id": appointment.id,
        "patient_id": appointment.patient_id,
        "doctor_id": appointment.doctor_id,
        "clinic_id": appointment.clinic_id,
        "reason": appointment.reason,
        "status": appointment.status,
        "appointment_date": appointment_date,
        "appointment_time": appointment.appointment_time,
    }


# 📌 Patient books appointment
@router.post("/", status_code=201, summary="Patient only: Book a new appointment")
def book_appointment(
    data: AppointmentCreate,
    db: Session = Depends(get_db),
    user=Depends(require_patient())
):

    doctor = db.query(User).filter(User.id == data.doctor_id, User.role == Roles.DOCTOR).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    clinic = db.query(Clinic).filter(Clinic.id == data.clinic_id).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")

    appointment = Appointment(
        patient_id=user["id"],
        doctor_id=data.doctor_id,
        clinic_id=data.clinic_id,
        reason=data.reason,
        appointment_date=data.appointment_date,
        appointment_time=data.appointment_time
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return {"message": "Appointment booked successfully", "appointment": _serialize_appointment(appointment)}


# 📌 Patient sees their appointments
@router.get("/my", response_model=list[AppointmentOut], summary="Patient only: List your appointments")
def my_appointments(
    db: Session = Depends(get_db),
    user=Depends(require_patient())
):
    results = db.query(Appointment).filter(Appointment.patient_id == user["id"]).all()
    return [_serialize_appointment(a) for a in results]


# 📌 Search appointments with optional filters
@router.get("/search", response_model=list[AppointmentOut], summary="Authenticated: Search appointments with filters")
def search_appointments(
    doctor_id: Optional[int] = None,
    patient_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    query = db.query(Appointment)

    if user["role"] == Roles.DOCTOR:
        query = query.filter(Appointment.doctor_id == user["id"])
    elif user["role"] == Roles.PATIENT:
        query = query.filter(Appointment.patient_id == user["id"])

    if doctor_id is not None:
        query = query.filter(Appointment.doctor_id == doctor_id)
    if patient_id is not None:
        query = query.filter(Appointment.patient_id == patient_id)
    if status is not None:
        query = query.filter(Appointment.status == status)
    if start_date is not None:
        query = query.filter(Appointment.appointment_date >= start_date)
    if end_date is not None:
        query = query.filter(Appointment.appointment_date <= end_date)

    results = query.all()
    return [_serialize_appointment(a) for a in results]


# 📌 Doctor sees their appointments
@router.get("/doctor", summary="Doctor only: List appointments assigned to you")
def doctor_appointments(
    db: Session = Depends(get_db),
    user=Depends(require_doctor())
):

    results = db.query(Appointment).filter(Appointment.doctor_id == user["id"]).all()
    return [_serialize_appointment(a) for a in results]


# 📌 Doctor approves appointment
@router.post("/{appointment_id}/approve", summary="Doctor only: Approve an appointment")
def approve_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_doctor())
):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id, Appointment.doctor_id == user["id"]).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appointment.status = "approved"
    db.commit()
    db.refresh(appointment)
    return {"message": "Appointment approved", "appointment": _serialize_appointment(appointment)}


# 📌 Doctor or admin completes appointment
@router.post("/{appointment_id}/complete", summary="Doctor or admin: Mark an appointment as completed")
def complete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user["role"] not in {Roles.DOCTOR, Roles.ADMIN}:
        raise HTTPException(status_code=403, detail="Access denied: insufficient permissions")

    query = db.query(Appointment).filter(Appointment.id == appointment_id)
    if user["role"] == Roles.DOCTOR:
        query = query.filter(Appointment.doctor_id == user["id"])

    appointment = query.first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment.status = "completed"
    db.commit()
    db.refresh(appointment)
    return {"message": "Appointment completed", "appointment": _serialize_appointment(appointment)}


# 📌 Patient cancels appointment
@router.post("/{appointment_id}/cancel", summary="Patient only: Cancel an appointment")
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_patient())
):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id, Appointment.patient_id == user["id"]).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appointment.status = "cancelled"
    db.commit()
    db.refresh(appointment)
    return {"message": "Appointment cancelled", "appointment": _serialize_appointment(appointment)}


# 📌 Admin sees all appointments
@router.get("/all", response_model=list[AppointmentOut], summary="Admin only: List all appointments")
def all_appointments(
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):

    results = db.query(Appointment).all()
    return [_serialize_appointment(a) for a in results]


# 📌 Patient reschedules appointment
@router.post("/{appointment_id}/reschedule", summary="Patient only: Reschedule an appointment")
def reschedule_appointment(
    appointment_id: int,
    data: AppointmentReschedule,
    db: Session = Depends(get_db),
    user=Depends(require_patient())
):
    """Patient only: Reschedule their appointment to a new date"""
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.patient_id == user["id"]
    ).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Cannot reschedule cancelled or completed appointments
    if appointment.status in ["cancelled", "completed"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot reschedule a {appointment.status} appointment"
        )
    
    old_date = appointment.appointment_date
    old_time = appointment.appointment_time
    appointment.appointment_date = data.appointment_date
    appointment.appointment_time = data.appointment_time
    
    # Reset status to pending after rescheduling
    appointment.status = "pending"
    
    db.commit()
    db.refresh(appointment)

    return {
        "message": "Appointment rescheduled successfully",
        "appointment_id": appointment_id,
        "old_date": old_date,
        "old_time": old_time,
        "new_date": appointment.appointment_date,
        "new_time": appointment.appointment_time,
        "appointment": _serialize_appointment(appointment)
    }
