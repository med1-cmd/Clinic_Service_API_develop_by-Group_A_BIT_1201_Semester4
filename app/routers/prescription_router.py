from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Prescription, User
from app.schemas.prescription import PrescriptionCreate, PrescriptionOut, PrescriptionUpdate
from app.deps import get_current_user, require_admin, require_doctor, require_patient
from app.constants import Roles

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])


# 🟢 Doctor creates prescription for a patient
@router.post("/", status_code=201, response_model=PrescriptionOut, summary="Doctor only: Create a new prescription")
def create_prescription(
    data: PrescriptionCreate,
    db: Session = Depends(get_db),
    user=Depends(require_doctor())
):
    patient = db.query(User).filter(User.id == data.patient_id, User.role == Roles.PATIENT).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    doctor = db.query(User).filter(User.id == data.doctor_id, User.role == Roles.DOCTOR).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    if user["id"] != data.doctor_id:
        raise HTTPException(status_code=403, detail="Doctor may only create prescriptions for themselves")

    prescription = Prescription(
        doctor_id=data.doctor_id,
        patient_id=data.patient_id,
        medication=data.medication,
        dosage=data.dosage,
        frequency=data.frequency,
        duration=data.duration,
        instructions=data.instructions
    )

    db.add(prescription)
    db.commit()
    db.refresh(prescription)

    return prescription


# 🟢 Patient sees their prescriptions
@router.get("/my", response_model=list[PrescriptionOut], summary="Patient only: List your prescriptions")
def my_prescriptions(
    db: Session = Depends(get_db),
    user=Depends(require_patient())
):
    return db.query(Prescription).filter(Prescription.patient_id == user["id"]).all()


# 🟢 Admin sees all prescriptions
@router.get("/all", response_model=list[PrescriptionOut], summary="Admin only: List all prescriptions")
def all_prescriptions(
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    return db.query(Prescription).all()


# 🟡 Doctor updates their prescription
@router.patch("/{prescription_id}", response_model=PrescriptionOut, summary="Doctor only: Update a prescription")
def update_prescription(
    prescription_id: int,
    data: PrescriptionUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_doctor())
):
    prescription = db.query(Prescription).filter(
        Prescription.id == prescription_id,
        Prescription.doctor_id == user["id"]
    ).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    if data.medication:
        prescription.medication = data.medication
    if data.dosage:
        prescription.dosage = data.dosage
    if data.instructions:
        prescription.instructions = data.instructions

    db.commit()
    db.refresh(prescription)
    return prescription


# 🔴 Doctor or admin deletes prescription
@router.delete("/{prescription_id}", summary="Doctor or admin: Delete a prescription")
def delete_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user["role"] not in {Roles.DOCTOR, Roles.ADMIN}:
        raise HTTPException(status_code=403, detail="Access denied: insufficient permissions")

    query = db.query(Prescription).filter(Prescription.id == prescription_id)
    if user["role"] == Roles.DOCTOR:
        query = query.filter(Prescription.doctor_id == user["id"])

    prescription = query.first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    db.delete(prescription)
    db.commit()
    return {"message": "Prescription deleted successfully", "prescription_id": prescription_id}
