# Clinic Service API MVP

A comprehensive FastAPI-based REST API MVP for managing healthcare services, including patient registration, doctor management, appointment scheduling, medical records, and prescription management with role-based access control (RBAC) and JWT authentication.

## Features

**User Authentication & Authorization**
- JWT token-based authentication
- OAuth2PasswordBearer implementation
- Role-based access control (RBAC)
- Three roles: Admin, Doctor, Patient

**CRUD Operations - All HTTP Methods**
- **Doctors**: Create, Read, Update, Delete, Search by specialty
- **Appointments**: Create, Read, Update status, Delete, Search with filters
- **Medical Records**: Create, Read, Update, Delete by authorized users
- **Prescriptions**: Create, Read, Update, Delete with role restrictions
- **Patients**: Manage patient information

**Appointment Management**
- Book appointments
- Status workflow: pending → approved → completed/cancelled
- Doctor approval system
- Patient cancellation
- Search and filter appointments

**Medical Records**
- Create comprehensive medical records
- Patient-accessible medical history
- Doctor records management
- Admin access to all records

**Prescription Management**
- Digital prescription system
- Doctor-created prescriptions
- Patient prescription access
- Medication tracking

**Dashboard Statistics**
- Admin system overview (patients, doctors, appointments)
- Doctor appointment statistics
- Patient engagement metrics
- Status-based reporting

**Async/Await Support**
- Asynchronous endpoints for notifications
- Health check endpoint with async operations
- Non-blocking I/O demonstration

**API Documentation**
- Automatic Swagger UI at `/docs`
- ReDoc documentation at `/redoc`
- Type hints and validation

---

## API Workflows

- **Authentication:** Register via `POST /auth/register`, then login via `POST /auth/login` to receive a JWT. Send the token in requests using the header `Authorization: Bearer <token>` for protected endpoints.
- **Appointment lifecycle:** Patient creates an appointment (`POST /appointments/`) — initial state `pending`. A doctor or admin can approve (`POST /appointments/{id}/approve`), then complete (`POST /appointments/{id}/complete`) or cancel (`POST /appointments/{id}/cancel`). Status changes should update related records and optionally trigger notifications.
- **Medical records:** Doctors create or update medical records via `POST /medical-records/` and `PATCH /medical-records/{id}`. Patients retrieve their records with `GET /medical-records/my`. Access is controlled by RBAC and ownership checks implemented in dependencies.
- **Prescriptions:** Doctors issue prescriptions (`POST /prescriptions/`); patients access them with `GET /prescriptions/my`. Prescriptions should include reference to the issuing doctor and appointment when applicable for auditability.

Developer extension checklist (how to replicate or extend):

1. Add or update models: define SQLAlchemy models in `app/models.py` and ensure migrations or `Base.metadata.create_all(bind=engine)` are run to apply schema changes.
2. Define Pydantic schemas: add request/response models in `app/schemas/` to maintain validation and documentation.
3. Create a router: add `app/routers/<resource>_router.py` with route handlers and dependency usage, then register it in `app/main.py` with `app.include_router()`.
4. Use dependencies: call `get_db()` for a scoped DB session and `get_current_user()` / `require_role()` for authentication/authorization inside route dependencies.
5. Tests & fixtures: follow `test_db.py` to create database fixtures; add endpoint tests under a `tests/` folder for CI coverage.

Developer notes:

- Prefer dependency-based role checks to centralize authorization logic.
- Keep routers focused and small to simplify testing and reviews.
- When introducing long-running or I/O-heavy tasks (notifications, reports), move them to background workers (Celery, RQ) rather than running in-request.

---

## MVP Scope
- Core user authentication and role-based access control (Admin, Doctor, Patient)
- CRUD operations for doctors, patients, appointments, medical records, and prescriptions
- Appointment booking and approval workflow
- Basic dashboard and statistics endpoints for admin and doctor users
- API docs via Swagger UI and ReDoc

## MVP Assumptions
- This MVP targets essential clinic workflows with secure access and role-based permissions.
- Advanced features like analytics, integrations, and extended notifications are reserved for later releases.
- The goal is a usable API foundation for core healthcare operations.

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| **Framework** | FastAPI 0.104+ |
| **Web Server** | Uvicorn |
| **Database** | PostgreSQL 12+ |
| **ORM** | SQLAlchemy 2.0+ |
| **Authentication** | JWT + OAuth2 |
| **Password Hashing** | Bcrypt |
| **Validation** | Pydantic v2 |
| **Environment** | Python-dotenv |

---

## Project Structure

```
clinic_service_api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── auth.py                 # Password hashing utilities
│   ├── database.py             # Database connection & session
│   ├── models.py               # SQLAlchemy ORM models
│   ├── deps.py                 # Dependency injection (auth, roles)
│   ├── constants.py            # Role constants
│   ├── schemas/                # Pydantic models
│   │   ├── user.py
│   │   ├── appointment.py
│   │   ├── doctor.py
│   │   ├── medical_record.py
│   │   ├── prescription.py
│   │   └── __init__.py
│   └── routers/                # API endpoints
│       ├── auth_router.py
│       ├── appointment_router.py
│       ├── doctor_router.py
│       ├── patient_router.py
│       ├── medical_record_router.py
│       ├── prescription_router.py
│       ├── dashboard_router.py
│       ├── notifications_router.py
│       └── __init__.py
├── docs/
│   ├── PROJECT_REPORT.md       # Comprehensive project report
│   ├── SDG_ALIGNMENT.md        # SDG 3 alignment documentation
├── .env.example                # Environment template
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## Installation & Setup

### Prerequisites
- Python 3.9 or higher
- PostgreSQL 12 or higher
- pip or conda

### Step 1: Clone & Setup Environment

```bash
git clone <repository-url>
cd clinic_service_api

python -m venv venv

venv\Scripts\activate
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

> If you are developing locally or want an installation path that enforces bcrypt/passlib compatibility, use:
>
> ```bash
> pip install -r requirements-dev.txt
> ```

### Step 3: Configure Environment

```bash
cp .env.example .env
```

### Step 4: Initialize Database

```bash
# Create database tables
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### Step 5: Run Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 6: Access API

- **API Base URL**: `http://localhost:8000`
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## API Endpoints Summary

### Authentication
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/register-admin` | Register a new admin | Admin |
| POST | `/auth/login` | Login (returns JWT token) | No |

### Users
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/users/` | List all users | Admin |
| GET | `/users/{user_id}` | Get user details | Admin |
| PATCH | `/users/{user_id}` | Update user | Admin |
| DELETE | `/users/{user_id}` | Delete user | Admin |

### Doctors
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/doctors/` | Create doctor | Admin |
| GET | `/doctors/` | List all doctors | Public |
| GET | `/doctors/search?specialty=` | Search doctors | Public |
| PATCH | `/doctors/{id}` | Update doctor | Admin |
| DELETE | `/doctors/{id}` | Delete doctor | Admin |
| POST | `/doctors/{doctor_id}/availability` | Add availability | Doctor |
| GET | `/doctors/{doctor_id}/availability` | Get availability | Public |
| PATCH | `/doctors/{doctor_id}/availability/{availability_id}` | Update availability | Doctor |
| DELETE | `/doctors/{doctor_id}/availability/{availability_id}` | Remove availability | Doctor |

### Admin Management
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/admins/` | Create admin | Admin |
| GET | `/admins/` | List all admins | Admin |
| GET | `/admins/{admin_id}` | Get admin details | Admin |
| PATCH | `/admins/{admin_id}` | Update admin | Admin |
| DELETE | `/admins/{admin_id}` | Delete admin | Admin |
| PATCH | `/admins/users/{user_id}/assign-role` | Assign role to user | Admin |
| POST | `/admins/users/{user_id}/permissions` | Set user permissions | Admin |
| GET | `/admins/users/` | List all users for management | Admin |
| GET | `/admins/clinics/summary` | Get clinics summary | Admin |
| GET | `/admins/doctors/summary` | Get doctors summary | Admin |
| GET | `/admins/platform/statistics` | Get platform statistics | Admin |
| POST | `/admins/platform/maintenance` | Toggle maintenance mode | Admin |

### Notifications
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/notifications/send-async` | Send async notification | Authenticated |
| GET | `/notifications/health-check` | Health check | Public |
| GET | `/notifications/prescription-alerts` | Get prescription alerts | Authenticated |
| POST | `/notifications/prescription-alerts/acknowledge/{id}` | Acknowledge prescription alert | Authenticated |

### Appointments
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/appointments/` | Book appointment | Patient |
| GET | `/appointments/my` | View own appointments | Patient |
| GET | `/appointments/doctor` | View doctor's appointments | Doctor |
| GET | `/appointments/all` | View all appointments | Admin |
| GET | `/appointments/search` | Search appointments | Authenticated |
| POST | `/appointments/{id}/approve` | Approve appointment | Doctor |
| POST | `/appointments/{id}/complete` | Complete appointment | Doctor/Admin |
| POST | `/appointments/{id}/cancel` | Cancel appointment | Patient |
| POST | `/appointments/{id}/reschedule` | Reschedule appointment | Patient |

### Clinics
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/clinics/` | Create clinic | Admin |
| GET | `/clinics/` | List all clinics | Public |
| GET | `/clinics/search` | Search clinics | Public |
| GET | `/clinics/{clinic_id}` | Clinic details | Public |
| GET | `/clinics/{clinic_id}/doctors` | Clinic doctors | Public |
| PATCH | `/clinics/{clinic_id}` | Update clinic | Admin |
| DELETE | `/clinics/{clinic_id}` | Delete clinic | Admin |

### Medical Records
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/medical-records/` | Create medical record | Doctor |
| GET | `/medical-records/` | List all records | Admin |
| GET | `/medical-records/patient/{patient_id}` | Patient records | Doctor/Admin |
| GET | `/medical-records/{record_id}` | Record details | Doctor/Admin |
| PATCH | `/medical-records/{record_id}` | Update record | Doctor |
| DELETE | `/medical-records/{record_id}` | Delete record | Doctor/Admin |

### Prescriptions
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/prescriptions/` | Create prescription | Doctor |
| GET | `/prescriptions/` | List all prescriptions | Admin |
| GET | `/prescriptions/patient/{patient_id}` | Patient prescriptions | Doctor/Admin |
| GET | `/prescriptions/{prescription_id}` | Prescription details | Doctor/Admin |
| PATCH | `/prescriptions/{prescription_id}` | Update prescription | Doctor |
| DELETE | `/prescriptions/{prescription_id}` | Delete prescription | Doctor/Admin |

## API Workflows
These workflows describe the common end-to-end usage patterns for the Clinic Service API.

### 1. Authentication Workflow
1. Register a user:
   - `POST /auth/register`
   - Body: `{ "email": "user@example.com", "password": "secret", "role": "patient" }`
2. Login to receive JWT:
   - `POST /auth/login`
   - Body: `{ "email": "user@example.com", "password": "secret" }`
   - Response contains `access_token`.
3. Use the JWT bearer token for protected endpoints:
   - Header: `Authorization: Bearer <access_token>`

### 2. Clinic Search Workflow
1. List all clinics:
   - `GET /clinics/`
2. Search local clinics by keyword:
   - `GET /clinics/search?name=health&specialty=dental&address=main`
3. Read clinic details:
   - `GET /clinics/{clinic_id}`
4. List doctors at a clinic:
   - `GET /clinics/{clinic_id}/doctors`

### 3. Doctor Discovery Workflow
1. List all doctors:
   - `GET /doctors/`
2. Search doctors by specialty:
   - `GET /doctors/search?specialty=cardiology`
3. Manage doctor assignments (Admin only):
   - `PUT /doctors/{doctor_id}/assign-clinic/{clinic_id}`

### 4. Appointment Booking Workflow
1. Patient creates an appointment:
   - `POST /appointments/`
   - Body example: `{ "doctor_id": 2, "patient_id": 5, "appointment_date": "2026-06-05T14:00:00", "reason": "Checkup" }`
2. Doctor reviews appointments:
   - `GET /appointments/doctor`
3. Doctor approves an appointment:
   - `POST /appointments/{id}/approve`
4. Complete or cancel:
   - `POST /appointments/{id}/complete` or `POST /appointments/{id}/cancel`

### 5. Medical Record Workflow
1. Doctor creates a medical record:
   - `POST /medical-records/`
   - Body includes `patient_id`, `doctor_id`, `diagnosis`, `prescriptions`, and notes.
2. Patient views history:
   - `GET /medical-records/patient`
3. Doctor views records for their patients:
   - `GET /medical-records/doctor`

### 6. Prescription Workflow
1. Doctor creates a prescription:
   - `POST /prescriptions/`
2. Patient retrieves own prescriptions:
   - `GET /prescriptions/patient`
3. Doctor updates or deletes prescriptions as needed.

### 7. Extension Workflow
To extend the API with new resources:
1. Add or update SQLAlchemy models in `app/models.py`.
2. Add Pydantic schemas in `app/schemas/`.
3. Create a router in `app/routers/` with CRUD/search endpoints.
4. Register the router in `app/main.py`.
5. Add any required authorization or dependency logic in `app/deps.py`.
6. Document the new endpoints and request shapes in this README.

### 8. Interactive API Docs
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

These workflows should help collaborators replicate the API behavior and extend the service search capabilities for local clinics.

### Medical Records
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/medical-records/` | Create record | Doctor |
| GET | `/medical-records/my` | View own records | Patient |
| GET | `/medical-records/doctor` | View doctor's records | Doctor |
| GET | `/medical-records/all` | View all records | Admin |
| PUT | `/medical-records/{id}` | Update record | Doctor |
| DELETE | `/medical-records/{id}` | Delete record | Doctor/Admin |

### Prescriptions
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/prescriptions/` | Create prescription | Doctor |
| GET | `/prescriptions/my` | View own prescriptions | Patient |
| GET | `/prescriptions/all` | View all prescriptions | Admin |
| PUT | `/prescriptions/{id}` | Update prescription | Doctor |
| DELETE | `/prescriptions/{id}` | Delete prescription | Doctor/Admin |

### Dashboard
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/dashboard/summary` | Admin system summary | Admin |
| GET | `/dashboard/doctor` | Doctor statistics | Doctor |
| GET | `/dashboard/patient` | Patient statistics | Patient |

### Notifications (Async Demo)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/notifications/send-async` | Send async notification | Authenticated |
| GET | `/notifications/health-check` | Async health check | Public |

---

## Authentication Flow

### 1. Register
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "email": "john@example.com",
    "password": "securepassword123",
    "role": "patient"
  }'
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john@example.com&password=securepassword123"
```

### 3. Use Token
```bash
curl -X GET "http://localhost:8000/appointments/my" \
  -H "Authorization: Bearer <your-jwt-token>"
```

---

## Role-Based Access Control

### Admin
- Full system access
- Create/update/delete doctors
- View all appointments, records, prescriptions
- Access dashboard summary

### Doctor
- Manage own appointments
- Create/update/delete own medical records
- Create/update/delete own prescriptions
- Access doctor dashboard
- Approve and complete appointments

### Patient
- Book appointments
- View own appointments
- View own medical records
- View own prescriptions
- Cancel appointments
- Access patient dashboard

---

## SDG Alignment

This project aligns with **UN Sustainable Development Goal 3: Good Health and Well-Being** by:

- Improving healthcare accessibility through digital systems
- Supporting patient record management
- Enabling appointment scheduling for better healthcare access
- Providing prescription tracking
- Supporting healthcare worker efficiency
- Enabling data-driven healthcare decisions

See [docs/SDG_ALIGNMENT.md](docs/SDG_ALIGNMENT.md) for detailed analysis.

---

## Testing

### Manual API Testing
1. Open Swagger UI: `http://localhost:8000/docs`
2. Click "Authorize" to login with JWT token
3. Test endpoints interactively

### Example Test Sequence
```bash
# 1. Register as patient
POST /auth/register
{
  "full_name": "Alice Patient",
  "email": "alice@clinic.com",
  "password": "password123",
  "role": "patient"
}

# 2. Register as doctor
POST /auth/register
{
  "full_name": "Dr. Bob",
  "email": "bob@clinic.com",
  "password": "password123",
  "role": "doctor",
  "specialty": "Cardiology",
  "license_number": "LICENSE123"
}

# 3. Login as patient
POST /auth/login
{
  "username": "alice@clinic.com",
  "password": "password123"
}

# 4. Book appointment
POST /appointments/
{
  "doctor_id": 2,
  "reason": "Heart checkup",
  "appointment_date": "2026-06-15T10:00:00"
}

# 5. View own appointments
GET /appointments/my

# 6. Doctor approves appointment
POST /appointments/1/approve
```

---

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5433/clinic_db

# JWT
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server (optional)
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

---

## Project Report

For comprehensive project documentation including:
- System architecture
- Technology justification
- Implementation details
- Challenges and solutions
- Future enhancements

See [docs/PROJECT_REPORT.md](docs/PROJECT_REPORT.md)

---

## Requirements Completion Checklist

- FastAPI Framework
- PostgreSQL + SQLAlchemy ORM
- Dependency Injection
- JWT Authentication & Authorization
- RBAC (Admin, Doctor, Patient)
- REST Standards (GET, POST, PUT, DELETE)
- CRUD Operations (Create, Read, Update, Delete)
- Swagger & ReDoc Documentation
- Type Annotations & Validation
- Async/Await Implementation
- SDG 3 Alignment Documentation

---

## Troubleshooting

### Database Connection Error
- Verify PostgreSQL is running
- Check DATABASE_URL in .env
- Ensure database exists

### JWT Token Error
- Token may be expired (default 30 minutes)
- Login again to get new token
- Check SECRET_KEY matches

### Port Already in Use
```bash
# Run on different port
uvicorn app.main:app --reload --port 8001
```

### Migration Issues
```bash
# Recreate database tables
python -c "from app.database import Base, engine; Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)"
```

---

## Contributing

1. Create feature branch: `git checkout -b feature/new-feature`
2. Commit changes: `git commit -am 'Add new feature'`
3. Push to branch: `git push origin feature/new-feature`
4. Submit pull request

---

## License

This project is licensed under the MIT License - see LICENSE file for details.

---

## Support & Documentation

- API Docs: `/docs` (Swagger UI)
- Alternative Docs: `/redoc` (ReDoc)
- Project Report: [docs/PROJECT_REPORT.md](docs/PROJECT_REPORT.md)
- SDG Alignment: [docs/SDG_ALIGNMENT.md](docs/SDG_ALIGNMENT.md)

---

**Version**: 1.0.0  
**Last Updated**: May 31, 2026  
**Status**: Production Ready
