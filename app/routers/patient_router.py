from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_admin
from app.models import User
from app.schemas import PatientCreate, PatientOut, PatientUpdate
from app.auth import hash_password
from app.constants import Roles

router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


@router.post("/register", status_code=201, response_model=PatientOut, summary="Public: Register a new patient")
def register_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(User).filter(User.email == patient.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_patient = User(
        full_name=patient.full_name,
        email=patient.email,
        password=hash_password(patient.password),
        role=Roles.PATIENT,
        phone=patient.phone,
        date_of_birth=patient.date_of_birth,
        gender=patient.gender
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return new_patient


@router.get("/", response_model=list[PatientOut], summary="Admin only: List all patients")
def get_patients(
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    return db.query(User).filter(User.role == Roles.PATIENT).all()


@router.patch("/{patient_id}", response_model=PatientOut, summary="Admin only: Update patient details")
def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    update_data = patient_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No update fields provided")

    for key, value in update_data.items():
        setattr(patient, key, value)

    db.commit()
    db.refresh(patient)

    return patient


@router.delete("/{patient_id}", summary="Admin only: Delete a patient")
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient").first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    db.delete(patient)
    db.commit()

    return {"message": "Patient deleted successfully"}
