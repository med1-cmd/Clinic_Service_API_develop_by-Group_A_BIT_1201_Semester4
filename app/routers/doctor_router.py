from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Clinic, User, DoctorAvailability
from app.schemas.doctor import (
    DoctorCreate, DoctorOut, DoctorInClinicOut, DoctorUpdate,
    DoctorAvailabilityCreate, DoctorAvailabilityUpdate, DoctorAvailabilityOut
)
from app.auth import hash_password
from app.deps import get_current_user, require_admin, require_doctor
from app.constants import Roles

router = APIRouter(prefix="/doctors", tags=["Doctors"])


def normalize_day_of_week(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("Invalid weekday")
    day = value.strip().title()
    valid_days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    if day not in valid_days:
        raise ValueError("Invalid day of week")
    return day


def expand_day_of_week(value: str) -> list[str]:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Invalid day of week")

    value = value.strip()
    if "-" in value:
        parts = [p.strip() for p in value.split("-") if p.strip()]
        if len(parts) != 2:
            raise ValueError("Invalid day of week range")
        start = normalize_day_of_week(parts[0])
        end = normalize_day_of_week(parts[1])
        weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        start_idx = weekdays.index(start)
        end_idx = weekdays.index(end)
        if end_idx < start_idx:
            raise ValueError("Invalid day of week range")
        return weekdays[start_idx:end_idx + 1]

    if "," in value:
        days = [normalize_day_of_week(part) for part in value.split(",") if part.strip()]
        if not days:
            raise ValueError("Invalid day of week")
        return days

    return [normalize_day_of_week(value)]


# 🟢 ADMIN: Create doctor
@router.post("/", status_code=201, response_model=DoctorOut, summary="Admin only: Create a new doctor")
def create_doctor(
    data: DoctorCreate,
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):

    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Doctor already exists")

    doctor = User(
        full_name=data.full_name,
        email=data.email,
        password=hash_password(data.password),
        role=Roles.DOCTOR,
        specialty=data.specialty,
        phone=data.phone,
        years_experience=data.years_experience,
        license_number=data.license_number
    )

    db.add(doctor)
    db.commit()
    db.refresh(doctor)

    return doctor


# 🟢 PUBLIC: List doctors
@router.get("/", response_model=list[DoctorOut], summary="Public: List all doctors")
def get_doctors(db: Session = Depends(get_db)):
    return db.query(User).filter(User.role == Roles.DOCTOR).all()


# 🟢 Search doctors by specialty
@router.get("/search", response_model=list[DoctorOut], summary="Public: Search doctors by specialty")
def search_doctors(specialty: str, db: Session = Depends(get_db)):
    return db.query(User).filter(
        User.role == Roles.DOCTOR,
        User.specialty.ilike(f"%{specialty}%")
    ).all()


# 🟡 ADMIN: Update doctor
@router.patch("/{doctor_id}", response_model=DoctorOut, summary="Admin only: Update a doctor's profile")
def update_doctor(
    doctor_id: int,
    data: DoctorUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    doctor = db.query(User).filter(User.id == doctor_id, User.role == Roles.DOCTOR).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    if data.id is not None:
        doctor.id = data.id
    if data.full_name:
        doctor.full_name = data.full_name
    if data.specialty:
        doctor.specialty = data.specialty
    if data.phone:
        doctor.phone = data.phone
    if data.years_experience is not None:
        doctor.years_experience = data.years_experience
    if data.license_number is not None:
        doctor.license_number = data.license_number
    if data.clinic_id is not None:
        doctor.clinic_id = data.clinic_id

    db.commit()
    db.refresh(doctor)
    return doctor


# 🟡 ADMIN: Assign doctor to a clinic
@router.patch("/{doctor_id}/assign-clinic/{clinic_id}", response_model=DoctorOut, summary="Admin only: Assign a doctor to a clinic")
def assign_doctor_to_clinic(
    doctor_id: int,
    clinic_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    doctor = db.query(User).filter(User.id == doctor_id, User.role == Roles.DOCTOR).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")

    doctor.clinic_id = clinic_id
    db.commit()
    db.refresh(doctor)
    return doctor


# 🔴 ADMIN: Delete doctor
@router.delete("/{doctor_id}", summary="Admin only: Delete a doctor")
def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    doctor = db.query(User).filter(User.id == doctor_id, User.role == Roles.DOCTOR).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    db.delete(doctor)
    db.commit()
    return {"message": "Doctor deleted successfully", "doctor_id": doctor_id}


# ==============================================================================
# Doctor Availability Management
# ==============================================================================

# 🟢 Doctor adds availability
@router.post("/{doctor_id}/availability", status_code=201, response_model=list[DoctorAvailabilityOut], summary="Doctor only: Add availability")
def add_doctor_availability(
    doctor_id: int,
    data: DoctorAvailabilityCreate,
    db: Session = Depends(get_db),
    user=Depends(require_doctor())
):
    """Doctor only: Add availability for a specific day or weekday range"""
    # Doctor can only set their own availability
    if user["id"] != doctor_id and user["role"] != Roles.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied")
    
    doctor = db.query(User).filter(User.id == doctor_id, User.role == Roles.DOCTOR).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    try:
        day_list = expand_day_of_week(data.day_of_week)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid day of week: {str(e)}")

    created_availabilities = []
    for day in day_list:
        existing = db.query(DoctorAvailability).filter(
            DoctorAvailability.doctor_id == doctor_id,
            DoctorAvailability.day_of_week == day
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Availability already exists for {day}")
        availability = DoctorAvailability(
            doctor_id=doctor_id,
            day_of_week=day,
            start_time=data.start_time,
            end_time=data.end_time,
        )
        db.add(availability)
        created_availabilities.append(availability)

    db.commit()
    for availability in created_availabilities:
        db.refresh(availability)

    return created_availabilities


# 🟢 PUBLIC: Get doctor availability
@router.get("/{doctor_id}/availability", response_model=list[DoctorAvailabilityOut], summary="Public: Get doctor availability")
def get_doctor_availability(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    """Public: Get availability schedule for a doctor"""
    doctor = db.query(User).filter(User.id == doctor_id, User.role == Roles.DOCTOR).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    return db.query(DoctorAvailability).filter(DoctorAvailability.doctor_id == doctor_id).all()


# 🟡 Doctor updates availability
@router.patch("/{doctor_id}/availability/{availability_id}", response_model=DoctorAvailabilityOut, summary="Doctor only: Update availability")
def update_doctor_availability(
    doctor_id: int,
    availability_id: int,
    data: DoctorAvailabilityUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_doctor())
):
    """Doctor only: Update their availability"""
    # Doctor can only update their own availability
    if user["id"] != doctor_id and user["role"] != Roles.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied")
    
    availability = db.query(DoctorAvailability).filter(
        DoctorAvailability.id == availability_id,
        DoctorAvailability.doctor_id == doctor_id
    ).first()
    
    if not availability:
        raise HTTPException(status_code=404, detail="Availability not found")
    
    if data.day_of_week:
        try:
            availability.day_of_week = normalize_day_of_week(data.day_of_week)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid day of week")
    
    if data.start_time:
        availability.start_time = data.start_time
    if data.end_time:
        availability.end_time = data.end_time
    
    db.commit()
    db.refresh(availability)
    
    return availability


# 🔴 Doctor removes availability
@router.delete("/{doctor_id}/availability/{availability_id}", summary="Doctor only: Remove availability")
def delete_doctor_availability(
    doctor_id: int,
    availability_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_doctor())
):
    """Doctor only: Remove their availability"""
    # Doctor can only delete their own availability
    if user["id"] != doctor_id and user["role"] != Roles.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied")
    
    availability = db.query(DoctorAvailability).filter(
        DoctorAvailability.id == availability_id,
        DoctorAvailability.doctor_id == doctor_id
    ).first()
    
    if not availability:
        raise HTTPException(status_code=404, detail="Availability not found")
    
    db.delete(availability)
    db.commit()
    
    return {"message": "Availability removed successfully", "availability_id": availability_id}
