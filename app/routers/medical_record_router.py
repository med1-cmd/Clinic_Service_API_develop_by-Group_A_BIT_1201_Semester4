from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import MedicalRecord, User
from app.schemas.medical_record import MedicalRecordCreate, MedicalRecordOut, MedicalRecordUpdate
from app.deps import get_current_user, require_admin, require_doctor, require_patient
from app.constants import Roles

router = APIRouter(prefix="/medical-records", tags=["Medical Records"])


# Doctor creates a medical record for a patient
@router.post("/", status_code=201, response_model=MedicalRecordOut, summary="Doctor only: Create a new medical record")
def create_medical_record(
    data: MedicalRecordCreate,
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
        raise HTTPException(status_code=403, detail="Doctor may only create records for themselves")

    record = MedicalRecord(
        patient_id=data.patient_id,
        doctor_id=data.doctor_id,
        diagnosis=data.diagnosis,
        treatment=data.treatment,
        notes=data.notes
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


# Patient views own medical records
@router.get("/my", response_model=list[MedicalRecordOut], summary="Patient only: List your medical records")
def my_medical_records(
    db: Session = Depends(get_db),
    user=Depends(require_patient())
):
    return db.query(MedicalRecord).filter(MedicalRecord.patient_id == user["id"]).all()


# Doctor views their medical records
@router.get("/doctor", response_model=list[MedicalRecordOut], summary="Doctor only: List your medical records")
def doctor_medical_records(
    db: Session = Depends(get_db),
    user=Depends(require_doctor())
):
    return db.query(MedicalRecord).filter(MedicalRecord.doctor_id == user["id"]).all()


# Admin views all medical records
@router.get("/all", response_model=list[MedicalRecordOut], summary="Admin only: List all medical records")
def all_medical_records(
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    return db.query(MedicalRecord).all()


# 🟡 Doctor updates their medical record
@router.patch("/{record_id}", response_model=MedicalRecordOut, summary="Doctor only: Update a medical record")
def update_medical_record(
    record_id: int,
    data: MedicalRecordUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_doctor())
):
    record = db.query(MedicalRecord).filter(
        MedicalRecord.id == record_id,
        MedicalRecord.doctor_id == user["id"]
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")

    if data.diagnosis:
        record.diagnosis = data.diagnosis
    if data.treatment:
        record.treatment = data.treatment
    if data.notes:
        record.notes = data.notes

    db.commit()
    db.refresh(record)
    return record


# 🔴 Doctor or admin deletes medical record
@router.delete("/{record_id}", summary="Doctor or admin: Delete a medical record")
def delete_medical_record(
    record_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user["role"] not in {Roles.DOCTOR, Roles.ADMIN}:
        raise HTTPException(status_code=403, detail="Access denied: insufficient permissions")

    query = db.query(MedicalRecord).filter(MedicalRecord.id == record_id)
    if user["role"] == Roles.DOCTOR:
        query = query.filter(MedicalRecord.doctor_id == user["id"])

    record = query.first()
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")

    db.delete(record)
    db.commit()
    return {"message": "Medical record deleted successfully", "record_id": record_id}
