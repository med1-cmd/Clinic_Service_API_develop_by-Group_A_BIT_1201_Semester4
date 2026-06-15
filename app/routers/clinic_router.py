from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Clinic, User
from app.schemas.clinic import ClinicCreate, ClinicUpdate
from app.schemas.doctor import DoctorInClinicOut
from app.deps import require_admin
from app.constants import Roles

router = APIRouter(
    prefix="/clinics",
    tags=["Clinics"]
)

@router.post("/", status_code=201, summary="Admin only: Create a new clinic")
def create_clinic(
    clinic: ClinicCreate,
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    """Admin only: Create a new clinic"""
    new_clinic = Clinic(**clinic.model_dump())

    db.add(new_clinic)
    db.commit()
    db.refresh(new_clinic)

    return new_clinic


@router.get("/", summary="Public: List all clinics")
def get_clinics(
    db: Session = Depends(get_db)
):
    """List all clinics"""
    return db.query(Clinic).all()


@router.get("/search", summary="Public: Search clinics by name, specialty, or address")
def search_clinics(
    name: str | None = None,
    specialty: str | None = None,
    address: str | None = None,
    db: Session = Depends(get_db)
):
    """Search clinics by name, specialty, or address"""
    query = db.query(Clinic)
    
    if name:
        query = query.filter(Clinic.name.ilike(f"%{name}%"))
    
    if specialty:
        query = query.filter(Clinic.specialty.ilike(f"%{specialty}%"))
    
    if address:
        query = query.filter(Clinic.address.ilike(f"%{address}%"))
    
    return query.all()


@router.get("/{clinic_id}", summary="Public: Get details for a clinic")
def get_clinic(
    clinic_id: int,
    db: Session = Depends(get_db)
):
    """Get clinic details by ID"""
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()
    
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    
    return clinic


@router.get("/{clinic_id}/doctors", response_model=list[DoctorInClinicOut], summary="Public: List doctors at a specific clinic")
def get_clinic_doctors(
    clinic_id: int,
    db: Session = Depends(get_db)
):
    """Get doctors assigned to a clinic"""
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")

    return db.query(User).filter(
        User.role == Roles.DOCTOR,
        User.clinic_id == clinic_id
    ).all()


@router.patch("/{clinic_id}", summary="Admin only: Update clinic details")
def update_clinic(
    clinic_id: int,
    clinic_update: ClinicUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    """Admin only: Update clinic details"""
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()
    
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    
    update_data = clinic_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(clinic, key, value)
    
    db.commit()
    db.refresh(clinic)
    
    return clinic


@router.delete("/{clinic_id}", summary="Admin only: Delete a clinic")
def delete_clinic(
    clinic_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    """Admin only: Delete a clinic"""
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()
    
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    
    db.delete(clinic)
    db.commit()
    
    return {"message": "Clinic deleted successfully"}

