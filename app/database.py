from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()
DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_user_columns():
    """Ensure the live users table contains the fields required by the current schema."""
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    existing_columns = {col["name"] for col in inspector.get_columns("users")}
    missing_columns = []

    if "phone" not in existing_columns:
        missing_columns.append("ALTER TABLE users ADD COLUMN phone VARCHAR")
    if "date_of_birth" not in existing_columns:
        missing_columns.append("ALTER TABLE users ADD COLUMN date_of_birth DATE")
    if "gender" not in existing_columns:
        missing_columns.append("ALTER TABLE users ADD COLUMN gender VARCHAR")
    if "years_experience" not in existing_columns:
        missing_columns.append("ALTER TABLE users ADD COLUMN years_experience INTEGER")

    if missing_columns:
        with engine.begin() as conn:
            for sql in missing_columns:
                conn.execute(text(sql))


def ensure_appointment_columns():
    """Ensure the live appointments table contains the fields required by the current schema."""
    inspector = inspect(engine)
    if "appointments" not in inspector.get_table_names():
        return

    existing_columns = {col["name"] for col in inspector.get_columns("appointments")}
    missing_columns = []

    if "patient_id" not in existing_columns:
        missing_columns.append("ALTER TABLE appointments ADD COLUMN patient_id INTEGER")
    if "doctor_id" not in existing_columns:
        missing_columns.append("ALTER TABLE appointments ADD COLUMN doctor_id INTEGER")
    if "clinic_id" not in existing_columns:
        missing_columns.append("ALTER TABLE appointments ADD COLUMN clinic_id INTEGER NOT NULL DEFAULT 0")
    if "reason" not in existing_columns:
        missing_columns.append("ALTER TABLE appointments ADD COLUMN reason VARCHAR NOT NULL DEFAULT ''")
    if "appointment_date" not in existing_columns:
        missing_columns.append("ALTER TABLE appointments ADD COLUMN appointment_date DATE NOT NULL DEFAULT '1970-01-01'")
    if "appointment_time" not in existing_columns:
        missing_columns.append("ALTER TABLE appointments ADD COLUMN appointment_time VARCHAR(8) NOT NULL DEFAULT '00:00'")
    if "status" not in existing_columns:
        missing_columns.append("ALTER TABLE appointments ADD COLUMN status VARCHAR NOT NULL DEFAULT 'pending'")
    if "created_at" not in existing_columns:
        missing_columns.append("ALTER TABLE appointments ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP")

    if missing_columns:
        with engine.begin() as conn:
            for sql in missing_columns:
                conn.execute(text(sql))


def ensure_prescription_columns():
    """Ensure the live prescriptions table contains the fields required by the current schema."""
    inspector = inspect(engine)
    if "prescriptions" not in inspector.get_table_names():
        return

    existing_columns = {col["name"] for col in inspector.get_columns("prescriptions")}
    missing_columns = []

    if "patient_id" not in existing_columns:
        missing_columns.append("ALTER TABLE prescriptions ADD COLUMN patient_id INTEGER NOT NULL DEFAULT 0")
    if "doctor_id" not in existing_columns:
        missing_columns.append("ALTER TABLE prescriptions ADD COLUMN doctor_id INTEGER NOT NULL DEFAULT 0")
    if "medication" not in existing_columns:
        missing_columns.append("ALTER TABLE prescriptions ADD COLUMN medication TEXT NOT NULL DEFAULT ''")
    if "dosage" not in existing_columns:
        missing_columns.append("ALTER TABLE prescriptions ADD COLUMN dosage TEXT NOT NULL DEFAULT ''")
    if "frequency" not in existing_columns:
        missing_columns.append("ALTER TABLE prescriptions ADD COLUMN frequency VARCHAR NOT NULL DEFAULT ''")
    if "duration" not in existing_columns:
        missing_columns.append("ALTER TABLE prescriptions ADD COLUMN duration VARCHAR NOT NULL DEFAULT ''")
    if "instructions" not in existing_columns:
        missing_columns.append("ALTER TABLE prescriptions ADD COLUMN instructions TEXT NOT NULL DEFAULT ''")
    if "created_at" not in existing_columns:
        missing_columns.append("ALTER TABLE prescriptions ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP")

    if missing_columns:
        with engine.begin() as conn:
            for sql in missing_columns:
                conn.execute(text(sql))


def ensure_clinic_columns():
    """Ensure the live clinics table contains the fields required by the current schema."""
    inspector = inspect(engine)
    if "clinics" not in inspector.get_table_names():
        return

    existing_columns = {col["name"] for col in inspector.get_columns("clinics")}
    missing_columns = []

    if "name" not in existing_columns:
        missing_columns.append("ALTER TABLE clinics ADD COLUMN name VARCHAR NOT NULL DEFAULT ''")
    if "address" not in existing_columns:
        missing_columns.append("ALTER TABLE clinics ADD COLUMN address VARCHAR NOT NULL DEFAULT ''")
    if "phone" not in existing_columns:
        missing_columns.append("ALTER TABLE clinics ADD COLUMN phone VARCHAR NOT NULL DEFAULT ''")
    if "email" not in existing_columns:
        missing_columns.append("ALTER TABLE clinics ADD COLUMN email VARCHAR NOT NULL DEFAULT ''")
    if "specialty" not in existing_columns:
        missing_columns.append("ALTER TABLE clinics ADD COLUMN specialty VARCHAR NOT NULL DEFAULT ''")
    if "description" not in existing_columns:
        missing_columns.append("ALTER TABLE clinics ADD COLUMN description VARCHAR")

    if missing_columns:
        with engine.begin() as conn:
            for sql in missing_columns:
                conn.execute(text(sql))