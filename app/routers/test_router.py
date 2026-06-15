from fastapi import APIRouter, Depends
from app.deps import require_role
from app.constants import Roles

router = APIRouter()

@router.get("/admin-only", summary="Admin only: Test admin-only access")
def admin_only(user=Depends(require_role(Roles.ADMIN))):
    return {"message": "Welcome Admin"}


@router.get("/doctor-only", summary="Doctor only: Test doctor-only access")
def doctor_only(user=Depends(require_role(Roles.DOCTOR))):
    return {"message": "Welcome Doctor"}
