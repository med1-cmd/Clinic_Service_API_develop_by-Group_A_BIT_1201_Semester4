from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine, ensure_user_columns, ensure_clinic_columns, ensure_appointment_columns, ensure_prescription_columns
from app import models

from app.routers.auth_router import router as auth_router
from app.routers.clinic_router import router as clinic_router
from app.routers.doctor_router import router as doctor_router
from app.routers.patient_router import router as patient_router
from app.routers.appointment_router import router as appointment_router
from app.routers.medical_record_router import router as medical_record_router
from app.routers.prescription_router import router as prescription_router
from app.routers.notifications_router import router as notifications_router
from app.routers.dashboard_router import router as dashboard_router
from app.routers.user_router import router as user_router
from app.routers.admin_router import router as admin_router
from app.routers.test_router import router as test_router
from app.routers.service_router import router as service_router
from app.routers.review_router import router as review_router

ensure_user_columns()
ensure_clinic_columns()
ensure_appointment_columns()
ensure_prescription_columns()
Base.metadata.create_all(bind=engine)

tags_metadata = [
    {
        "name": "Authentication",
        "description": "User authentication endpoints",
    },
    {
        "name": "User Management",
        "description": "User management operations",
    },
    {
        "name": "Admin Management",
        "description": "Admin management operations",
    },
    {
        "name": "Clinics",
        "description": "Clinic operations",
    },
    {
        "name": "Doctors",
        "description": "Doctor operations",
    },
    {
        "name": "Patients",
        "description": "Patient operations",
    },
    {
        "name": "Appointments",
        "description": "Appointment scheduling and management",
    },
    {
        "name": "Medical Records",
        "description": "Medical records operations",
    },
    {
        "name": "Prescriptions",
        "description": "Prescription operations",
    },
    {
        "name": "Services",
        "description": "Service operations",
    },
    {
        "name": "Reviews",
        "description": "Review operations",
    },
    {
        "name": "Notifications",
        "description": "Notification operations",
    },
    {
        "name": "Dashboard",
        "description": "Dashboard and analytics",
    },
]

app = FastAPI(
    title="Clinic Service API MVP",
    description="SDG 3: Good Health and Well-Being",
    version="1.0.0",
    openapi_tags=tags_metadata
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body = await request.body()
    body_text = body.decode("utf-8", errors="replace") if body else ""
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "request_method": request.method,
            "request_url": str(request.url),
            "request_body": body_text,
        },
    )

app.include_router(auth_router)
app.include_router(clinic_router)
app.include_router(doctor_router)
app.include_router(patient_router)
app.include_router(appointment_router)
app.include_router(medical_record_router)
app.include_router(prescription_router)
app.include_router(notifications_router)
app.include_router(dashboard_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(test_router)
app.include_router(service_router)
app.include_router(review_router)


@app.get("/")
def home():
    return {
        "message": "Clinic Service API Running Successfully"
    }