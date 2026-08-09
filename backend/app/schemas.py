import uuid
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.utils.validators import (
    validate_name, validate_dob, validate_sex,
    validate_phone, validate_state, validate_zip, validate_email
)

class PatientBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    sex: str
    phone_number: str
    email: Optional[str] = None
    address_line_1: str
    address_line_2: Optional[str] = None
    city: str
    state: str
    zip_code: str
    insurance_provider: Optional[str] = None
    insurance_member_id: Optional[str] = None
    preferred_language: str = "English"
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    sex: str
    phone_number: str
    email: Optional[str] = None
    address_line_1: str
    address_line_2: Optional[str] = None
    city: str
    state: str
    zip_code: str
    insurance_provider: Optional[str] = None
    insurance_member_id: Optional[str] = None
    preferred_language: str = "English"
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    @field_validator("first_name")
    @classmethod
    def check_first_name(cls, v):
        return validate_name(v, "first_name")

    @field_validator("last_name")
    @classmethod
    def check_last_name(cls, v):
        return validate_name(v, "last_name")

    @field_validator("date_of_birth", mode="before")
    @classmethod
    def check_dob(cls, v):
        return validate_dob(v)

    @field_validator("sex")
    @classmethod
    def check_sex(cls, v):
        return validate_sex(v)

    @field_validator("phone_number")
    @classmethod
    def check_phone(cls, v):
        return validate_phone(v, "phone_number", required=True)

    @field_validator("state")
    @classmethod
    def check_state(cls, v):
        return validate_state(v)

    @field_validator("zip_code")
    @classmethod
    def check_zip(cls, v):
        return validate_zip(v)

    @field_validator("email")
    @classmethod
    def check_email(cls, v):
        return validate_email(v)

    @field_validator("emergency_contact_phone")
    @classmethod
    def check_emergency_phone(cls, v):
        return validate_phone(v, "emergency_contact_phone", required=False)

class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    sex: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_member_id: Optional[str] = None
    preferred_language: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    @field_validator("first_name")
    @classmethod
    def check_first_name(cls, v):
        if v is None:
            return v
        return validate_name(v, "first_name")

    @field_validator("last_name")
    @classmethod
    def check_last_name(cls, v):
        if v is None:
            return v
        return validate_name(v, "last_name")

    @field_validator("date_of_birth", mode="before")
    @classmethod
    def check_dob(cls, v):
        if v is None:
            return v
        return validate_dob(v)

    @field_validator("sex")
    @classmethod
    def check_sex(cls, v):
        if v is None:
            return v
        return validate_sex(v)

    @field_validator("phone_number")
    @classmethod
    def check_phone(cls, v):
        if v is None:
            return v
        return validate_phone(v, "phone_number", required=True)

    @field_validator("state")
    @classmethod
    def check_state(cls, v):
        if v is None:
            return v
        return validate_state(v)

    @field_validator("zip_code")
    @classmethod
    def check_zip(cls, v):
        if v is None:
            return v
        return validate_zip(v)

    @field_validator("email")
    @classmethod
    def check_email(cls, v):
        if v is None:
            return v
        return validate_email(v)

    @field_validator("emergency_contact_phone")
    @classmethod
    def check_emergency_phone(cls, v):
        if v is None:
            return v
        return validate_phone(v, "emergency_contact_phone", required=False)

class PatientResponse(PatientBase):
    patient_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

class CallTranscriptResponse(BaseModel):
    id: uuid.UUID
    patient_id: Optional[uuid.UUID]
    vapi_call_id: str
    caller_phone_number: Optional[str] = None
    transcript: Optional[str] = None
    call_summary: Optional[str] = None
    call_status: Optional[str] = None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

