from pydantic import BaseModel, field_serializer, field_validator, model_validator
from .base import NoIdCreateModel, NoIdUpdateModel
from datetime import datetime


class DoctorCreate(NoIdCreateModel):
    full_name: str
    email: str
    password: str
    specialty: str
    phone: str
    years_experience: int
    license_number: str


class DoctorUpdate(BaseModel):
    model_config = {
        "extra": "forbid"
    }

    id: int | None = None
    full_name: str | None = None
    specialty: str | None = None
    phone: str | None = None
    years_experience: int | None = None
    license_number: str | None = None
    clinic_id: int | None = None


class DoctorOut(BaseModel):
    id: int
    full_name: str
    email: str
    specialty: str
    phone: str | None = None
    years_experience: int | None = None
    license_number: str | None = None
    clinic_id: int | None = None

    class Config:
        from_attributes = True


class DoctorInClinicOut(BaseModel):
    id: int
    full_name: str
    specialty: str | None = None
    license_number: str | None = None

    class Config:
        from_attributes = True


class DoctorAvailabilityCreate(BaseModel):
    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "example": {
                "day_of_week": "Monday",
                "start_time": "9:00 AM",
                "end_time": "5:00 PM"
            }
        }
    }
    day_of_week: str  # Monday, Tuesday, etc.
    start_time: str   # 12-hour format with AM/PM (e.g., "9:00 AM")
    end_time: str     # 12-hour format with AM/PM (e.g., "5:00 PM")

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def validate_and_normalize_time(cls, v: str) -> str:
        """
        Validate 12-hour time format with AM/PM and convert to 24-hour HH:MM.
        Accepts: "9:00 AM", "9:00 am", "09:00 AM", etc.
        Returns: "09:00", "17:00", etc.
        """
        if not isinstance(v, str):
            raise ValueError("Time must be a string")
        
        v = v.strip()
        
        # Check if AM/PM is present
        if not any(v.upper().endswith(suffix) for suffix in ("AM", "PM")):
            raise ValueError("Time must include AM or PM (e.g., '9:00 AM')")
        
        # Try to parse as 12-hour time
        for fmt in ("%I:%M %p", "%I:%M%p"):
            try:
                parsed_time = datetime.strptime(v.upper(), fmt)
                return parsed_time.strftime("%H:%M")
            except ValueError:
                continue
        
        raise ValueError("Invalid time format. Use 12-hour format with AM/PM (e.g., '9:00 AM')")

    @model_validator(mode="after")
    def validate_end_time_after_start_time(self):
        """Ensure end_time is after start_time."""
        if self.start_time and self.end_time:
            start = datetime.strptime(self.start_time, "%H:%M")
            end = datetime.strptime(self.end_time, "%H:%M")
            if end <= start:
                raise ValueError("end_time must be after start_time")
        return self


class DoctorAvailabilityUpdate(BaseModel):
    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "example": {
                "day_of_week": "Tuesday",
                "start_time": "10:00 AM",
                "end_time": "6:00 PM"
            }
        }
    }
    day_of_week: str | None = None
    start_time: str | None = None   # 12-hour format with AM/PM
    end_time: str | None = None     # 12-hour format with AM/PM

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def validate_and_normalize_time(cls, v: str | None) -> str | None:
        """
        Validate 12-hour time format with AM/PM and convert to 24-hour HH:MM.
        """
        if v is None:
            return None
            
        if not isinstance(v, str):
            raise ValueError("Time must be a string")
        
        v = v.strip()
        
        # Check if AM/PM is present
        if not any(v.upper().endswith(suffix) for suffix in ("AM", "PM")):
            raise ValueError("Time must include AM or PM (e.g., '9:00 AM')")
        
        # Try to parse as 12-hour time
        for fmt in ("%I:%M %p", "%I:%M%p"):
            try:
                parsed_time = datetime.strptime(v.upper(), fmt)
                return parsed_time.strftime("%H:%M")
            except ValueError:
                continue
        
        raise ValueError("Invalid time format. Use 12-hour format with AM/PM (e.g., '9:00 AM')")

    @model_validator(mode="after")
    def validate_end_time_after_start_time(self):
        """Ensure end_time is after start_time if both are provided."""
        if self.start_time and self.end_time:
            start = datetime.strptime(self.start_time, "%H:%M")
            end = datetime.strptime(self.end_time, "%H:%M")
            if end <= start:
                raise ValueError("end_time must be after start_time")
        return self


class DoctorAvailabilityOut(BaseModel):
    id: int
    doctor_id: int
    day_of_week: str
    start_time: str
    end_time: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 2,
                "doctor_id": 2,
                "day_of_week": "Monday",
                "start_time": "09:00 AM",
                "end_time": "05:30 PM"
            }
        }
    }

    @field_serializer("start_time", "end_time")
    def format_time(self, value: str) -> str:
        parsed_time = datetime.strptime(value, "%H:%M")
        return parsed_time.strftime("%I:%M %p")
