from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Appointment, Clinic, MedicalRecord, Prescription, User
from app.deps import get_current_user, require_admin, require_doctor, require_patient
from app.constants import Roles

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", summary="Admin only: Get global dashboard summary")
def admin_summary(
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    total_patients = db.query(User).filter(User.role == Roles.PATIENT).count()
    total_doctors = db.query(User).filter(User.role == Roles.DOCTOR).count()
    total_appointments = db.query(Appointment).count()
    appointment_status_counts = {
        status: count
        for status, count in db.query(Appointment.status, func.count(Appointment.id)).group_by(Appointment.status).all()
    }
    upcoming_appointments = db.query(Appointment).filter(Appointment.appointment_date >= func.now()).count()
    medical_record_count = db.query(MedicalRecord).count()
    prescription_count = db.query(Prescription).count()

    return {
        "total_patients": total_patients,
        "total_doctors": total_doctors,
        "total_appointments": total_appointments,
        "appointment_status_counts": appointment_status_counts,
        "upcoming_appointments": upcoming_appointments,
        "medical_record_count": medical_record_count,
        "prescription_count": prescription_count,
    }


@router.get("/clinic-summary", summary="Admin only: Get clinic-level dashboard summary")
def clinic_summary(
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    total_users = db.query(User).count()
    total_patients = db.query(User).filter(User.role == Roles.PATIENT).count()
    total_doctors = db.query(User).filter(User.role == Roles.DOCTOR).count()
    total_clinics = db.query(Clinic).count()
    total_appointments = db.query(Appointment).count()
    total_medical_records = db.query(MedicalRecord).count()
    total_prescriptions = db.query(Prescription).count()

    return {
        "total_users": total_users,
        "total_patients": total_patients,
        "total_doctors": total_doctors,
        "total_clinics": total_clinics,
        "total_appointments": total_appointments,
        "total_medical_records": total_medical_records,
        "total_prescriptions": total_prescriptions,
    }


@router.get("/doctor", summary="Doctor only: Get your appointment metrics")
def doctor_summary(
    db: Session = Depends(get_db),
    user=Depends(require_doctor())
):
    total_appointments = db.query(Appointment).filter(Appointment.doctor_id == user["id"]).count()
    status_counts = {
        status: count
        for status, count in db.query(Appointment.status, func.count(Appointment.id))
            .filter(Appointment.doctor_id == user["id"])
            .group_by(Appointment.status)
            .all()
    }
    upcoming_appointments = db.query(Appointment).filter(
        Appointment.doctor_id == user["id"],
        Appointment.appointment_date >= func.now()
    ).count()

    return {
        "doctor_id": user["id"],
        "total_appointments": total_appointments,
        "appointment_status_counts": status_counts,
        "upcoming_appointments": upcoming_appointments,
    }


@router.get("/patient", summary="Patient only: Get your appointment and prescription metrics")
def patient_summary(
    db: Session = Depends(get_db),
    user=Depends(require_patient())
):
    total_appointments = db.query(Appointment).filter(Appointment.patient_id == user["id"]).count()
    status_counts = {
        status: count
        for status, count in db.query(Appointment.status, func.count(Appointment.id))
            .filter(Appointment.patient_id == user["id"])
            .group_by(Appointment.status)
            .all()
    }
    upcoming_appointments = db.query(Appointment).filter(
        Appointment.patient_id == user["id"],
        Appointment.appointment_date >= func.now()
    ).count()
    prescription_count = db.query(Prescription).filter(Prescription.patient_id == user["id"]).count()

    return {
        "patient_id": user["id"],
        "total_appointments": total_appointments,
        "appointment_status_counts": status_counts,
        "upcoming_appointments": upcoming_appointments,
        "prescription_count": prescription_count,
    }
