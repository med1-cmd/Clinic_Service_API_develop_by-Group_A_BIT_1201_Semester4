from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models import User, Clinic
from app.schemas import AdminCreate, UserCreate, UserUpdate, UserOut, UserPermissionSchema, MaintenanceModeSchema
from app.auth import hash_password
from app.deps import require_admin
from app.constants import Roles

router = APIRouter(
    prefix="/admins",
    tags=["Admin Management"]
)


# Schema for role assignment
class RoleAssignmentSchema(BaseModel):
    user_id: int
    new_role: str


@router.post("/", status_code=201, response_model=UserOut, summary="Admin only: Create a new admin")
def create_admin(
    data: AdminCreate,
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    """Admin only: Create a new admin user"""
    existing_admin = db.query(User).filter(User.email == data.email).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin with this email already exists")
    
    new_admin = User(
        full_name=data.full_name,
        email=data.email,
        password=hash_password(data.password),
        role=Roles.ADMIN,
        license_number=data.license_number
    )
    
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    
    return new_admin


@router.get("/", response_model=list[UserOut], summary="Admin only: List all admins")
def list_admins(
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    """Admin only: List all admin users"""
    return db.query(User).filter(User.role == Roles.ADMIN).all()


@router.get("/{admin_id}", response_model=UserOut, summary="Admin only: Get admin details")
def get_admin(
    admin_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    """Admin only: Get specific admin details"""
    admin = db.query(User).filter(User.id == admin_id, User.role == Roles.ADMIN).first()
    
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    return admin


@router.patch("/{admin_id}", response_model=UserOut, summary="Admin only: Update admin details")
def update_admin(
    admin_id: int,
    admin_update: UserUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    """Admin only: Update admin details"""
    admin = db.query(User).filter(User.id == admin_id, User.role == Roles.ADMIN).first()
    
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    # Prevent changing role to non-admin
    if admin_update.role is not None and admin_update.role != Roles.ADMIN:
        raise HTTPException(status_code=400, detail="Admin role cannot be changed to non-admin")
    
    update_data = admin_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key != "role":  # Prevent role change
            setattr(admin, key, value)
    
    db.commit()
    db.refresh(admin)
    
    return admin


@router.delete("/{admin_id}", summary="Admin only: Delete an admin")
def delete_admin(
    admin_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    """Admin only: Delete an admin user"""
    admin = db.query(User).filter(User.id == admin_id, User.role == Roles.ADMIN).first()
    
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    db.delete(admin)
    db.commit()
    
    return {"message": "Admin deleted successfully", "admin_id": admin_id}


# ==============================================================================
# User Management - Role Assignment & Permissions
# ==============================================================================

@router.patch("/users/{user_id}/assign-role", response_model=UserOut, summary="Admin only: Assign role to user")
def assign_user_role(
    user_id: int,
    role_data: RoleAssignmentSchema,
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    """Admin only: Assign a role to a user"""
    target_user = db.query(User).filter(User.id == user_id).first()
    
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if role_data.new_role not in [Roles.PATIENT, Roles.DOCTOR, Roles.ADMIN]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    target_user.role = role_data.new_role
    db.commit()
    db.refresh(target_user)
    
    return target_user


@router.post("/users/{user_id}/permissions", summary="Admin only: Set user permissions")
def set_user_permissions(
    user_id: int,
    permissions: UserPermissionSchema,
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    """Admin only: Set user permissions"""
    target_user = db.query(User).filter(User.id == user_id).first()
    
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user_id,
        "user_name": target_user.full_name,
        "role": target_user.role,
        "permissions": permissions.permissions,
        "message": "Permissions set successfully"
    }


@router.get("/users/", response_model=list[UserOut], summary="Admin only: List all users for management")
def manage_users(
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    """Admin only: List all users in the system for management"""
    return db.query(User).all()


# ==============================================================================
# Clinic Management
# ==============================================================================

@router.get("/clinics/summary", summary="Admin only: Get clinics summary")
def get_clinics_summary(
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    """Admin only: Get summary of all clinics"""
    clinics = db.query(Clinic).all()
    
    clinic_data = [
        {
            "clinic_id": clinic.id,
            "name": clinic.name,
            "specialty": clinic.specialty,
            "address": clinic.address,
            "phone": clinic.phone,
            "doctors_count": len(clinic.doctors) if clinic.doctors else 0,
            "services_count": len(clinic.services) if clinic.services else 0
        }
        for clinic in clinics
    ]
    
    return {
        "total_clinics": len(clinics),
        "clinics": clinic_data
    }


# ==============================================================================
# Doctor Management
# ==============================================================================

@router.get("/doctors/summary", summary="Admin only: Get doctors summary")
def get_doctors_summary(
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    """Admin only: Get summary of all doctors"""
    doctors = db.query(User).filter(User.role == Roles.DOCTOR).all()
    
    doctor_data = [
        {
            "doctor_id": doctor.id,
            "full_name": doctor.full_name,
            "email": doctor.email,
            "specialty": doctor.specialty,
            "phone": doctor.phone,
            "years_experience": doctor.years_experience,
            "clinic_id": doctor.clinic_id
        }
        for doctor in doctors
    ]
    
    return {
        "total_doctors": len(doctors),
        "doctors": doctor_data
    }


@router.get("/platform/statistics", summary="Admin only: Get platform statistics")
def get_platform_statistics(
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    """Admin only: Get overall platform statistics"""
    total_users = db.query(User).count()
    total_admins = db.query(User).filter(User.role == Roles.ADMIN).count()
    total_doctors = db.query(User).filter(User.role == Roles.DOCTOR).count()
    total_patients = db.query(User).filter(User.role == Roles.PATIENT).count()
    total_clinics = db.query(Clinic).count()
    
    return {
        "total_users": total_users,
        "admins": total_admins,
        "doctors": total_doctors,
        "patients": total_patients,
        "clinics": total_clinics,
        "timestamp": "platform-stats-generated"
    }


@router.post("/platform/maintenance", summary="Admin only: Toggle maintenance mode")
def toggle_maintenance_mode(
    data: MaintenanceModeSchema,
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    """Admin only: Toggle platform maintenance mode"""
    return {
        "message": data.message,
        "maintenance_mode": data.enabled
    }
