from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Service
from app.schemas import ServiceCreate, ServiceUpdate, ServiceOut
from app.deps import require_admin


router = APIRouter(
    prefix="/services",
    tags=["Services"]
)


@router.post("/", status_code=201, response_model=ServiceOut, summary="Admin only: Create a service")
def create_service(
    service: ServiceCreate,
    db: Session = Depends(get_db),
    user=Depends(require_admin())
):
    new = Service(**service.model_dump())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


@router.get("/", response_model=list[ServiceOut], summary="List all services")
def list_services(db: Session = Depends(get_db)):
    return db.query(Service).all()


@router.get("/clinic/{clinic_id}", response_model=list[ServiceOut], summary="List services for a clinic")
def services_for_clinic(clinic_id: int, db: Session = Depends(get_db)):
    return db.query(Service).filter(Service.clinic_id == clinic_id).all()


@router.get("/{service_id}", response_model=ServiceOut, summary="Get service by id")
def get_service(service_id: int, db: Session = Depends(get_db)):
    svc = db.query(Service).filter(Service.id == service_id).first()
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    return svc


@router.patch("/{service_id}", response_model=ServiceOut, summary="Admin only: Update a service")
def update_service(service_id: int, service_update: ServiceUpdate, db: Session = Depends(get_db), user=Depends(require_admin())):
    svc = db.query(Service).filter(Service.id == service_id).first()
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    data = service_update.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(svc, k, v)
    db.commit()
    db.refresh(svc)
    return svc


@router.delete("/{service_id}", summary="Admin only: Delete a service")
def delete_service(service_id: int, db: Session = Depends(get_db), user=Depends(require_admin())):
    svc = db.query(Service).filter(Service.id == service_id).first()
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(svc)
    db.commit()
    return {"message": "Service deleted"}
