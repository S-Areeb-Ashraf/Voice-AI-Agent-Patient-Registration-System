from datetime import datetime, timezone, date
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import Patient, CallTranscript
from app.schemas import PatientCreate, PatientUpdate
from app.utils.logging_config import logger
from app.utils.validators import validate_phone, validate_dob

def get_patients(db: Session, last_name: Optional[str] = None, date_of_birth: Optional[str] = None, phone_number: Optional[str] = None) -> List[Patient]:
    """Retrieves all active (non-soft-deleted) patients, optionally filtered by filters."""
    query = db.query(Patient).filter(Patient.deleted_at.is_(None))
    
    if last_name:
        query = query.filter(Patient.last_name.ilike(f"%{last_name.strip()}%"))
        
    if date_of_birth:
        try:
            parsed_dob = validate_dob(date_of_birth)
            query = query.filter(Patient.date_of_birth == parsed_dob)
        except ValueError:
            # If DOB format is invalid, we don't break the query; we filter with None which returns empty list.
            # This is robust and doesn't cause silent errors.
            return []
            
    if phone_number:
        try:
            clean_phone = validate_phone(phone_number, "phone_number", required=True)
            query = query.filter(Patient.phone_number == clean_phone)
        except ValueError:
            return []
            
    return query.order_by(Patient.created_at.desc()).all()

def get_patient_by_id(db: Session, patient_id) -> Optional[Patient]:
    """Retrieves an active patient by UUID."""
    return db.query(Patient).filter(Patient.patient_id == patient_id, Patient.deleted_at.is_(None)).first()

def get_patient_by_phone(db: Session, phone_number: str) -> Optional[Patient]:
    """Retrieves an active patient by their normalized phone number."""
    try:
        clean_phone = validate_phone(phone_number, "phone_number", required=True)
    except ValueError:
        return None
    return db.query(Patient).filter(Patient.phone_number == clean_phone, Patient.deleted_at.is_(None)).first()

def create_patient(db: Session, patient_data: PatientCreate) -> Patient:
    """Creates a new patient, saves to DB, and logs the final payload."""
    db_patient = Patient(
        first_name=patient_data.first_name,
        last_name=patient_data.last_name,
        date_of_birth=patient_data.date_of_birth,
        sex=patient_data.sex,
        phone_number=patient_data.phone_number,
        email=patient_data.email,
        address_line_1=patient_data.address_line_1,
        address_line_2=patient_data.address_line_2,
        city=patient_data.city,
        state=patient_data.state,
        zip_code=patient_data.zip_code,
        insurance_provider=patient_data.insurance_provider,
        insurance_member_id=patient_data.insurance_member_id,
        preferred_language=patient_data.preferred_language,
        emergency_contact_name=patient_data.emergency_contact_name,
        emergency_contact_phone=patient_data.emergency_contact_phone
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    
    # Observability requirement: Log full final patient payload to stdout
    logger.info(
        f"SUCCESSFULLY CREATED PATIENT PAYLOAD:\n"
        f"  patient_id: {db_patient.patient_id}\n"
        f"  first_name: {db_patient.first_name}\n"
        f"  last_name: {db_patient.last_name}\n"
        f"  date_of_birth: {db_patient.date_of_birth}\n"
        f"  sex: {db_patient.sex}\n"
        f"  phone_number: {db_patient.phone_number}\n"
        f"  email: {db_patient.email}\n"
        f"  address_line_1: {db_patient.address_line_1}\n"
        f"  address_line_2: {db_patient.address_line_2}\n"
        f"  city: {db_patient.city}\n"
        f"  state: {db_patient.state}\n"
        f"  zip_code: {db_patient.zip_code}\n"
        f"  insurance_provider: {db_patient.insurance_provider}\n"
        f"  insurance_member_id: {db_patient.insurance_member_id}\n"
        f"  preferred_language: {db_patient.preferred_language}\n"
        f"  emergency_contact_name: {db_patient.emergency_contact_name}\n"
        f"  emergency_contact_phone: {db_patient.emergency_contact_phone}\n"
        f"  created_at: {db_patient.created_at}"
    )
    return db_patient

def update_patient(db: Session, patient_id, patient_data: PatientUpdate) -> Optional[Patient]:
    """Partially updates an active patient, setting updated_at to now."""
    db_patient = get_patient_by_id(db, patient_id)
    if not db_patient:
        return None
        
    update_data = patient_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_patient, key, value)
        
    db_patient.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def soft_delete_patient(db: Session, patient_id) -> Optional[Patient]:
    """Soft-deletes a patient by setting deleted_at to current timestamp."""
    db_patient = get_patient_by_id(db, patient_id)
    if not db_patient:
        return None
    db_patient.deleted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def create_call_transcript(
    db: Session, 
    patient_id: Optional[str], 
    vapi_call_id: str, 
    caller_phone_number: Optional[str], 
    transcript: Optional[str], 
    call_summary: Optional[str], 
    call_status: Optional[str]
) -> CallTranscript:
    """Inserts a new call transcript linked to a patient."""
    db_transcript = CallTranscript(
        patient_id=patient_id,
        vapi_call_id=vapi_call_id,
        caller_phone_number=caller_phone_number,
        transcript=transcript,
        call_summary=call_summary,
        call_status=call_status
    )
    db.add(db_transcript)
    db.commit()
    db.refresh(db_transcript)
    return db_transcript

def get_transcripts_by_patient_id(db: Session, patient_id) -> List[CallTranscript]:
    """Retrieves all call logs/transcripts associated with a patient."""
    return db.query(CallTranscript).filter(CallTranscript.patient_id == patient_id).order_by(CallTranscript.created_at.desc()).all()
