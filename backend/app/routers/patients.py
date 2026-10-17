import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import PatientCreate, PatientUpdate, PatientResponse, CallTranscriptResponse
from app.services import patient_service

router = APIRouter(prefix="/patients", tags=["patients"])

@router.get("")
def read_patients(
    last_name: Optional[str] = None,
    date_of_birth: Optional[str] = None,
    phone_number: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        patients = patient_service.get_patients(db, last_name, date_of_birth, phone_number)
        data = [PatientResponse.model_validate(p) for p in patients]
        return {"data": data, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}

@router.get("/{patient_id}")
def read_patient(patient_id: uuid.UUID, db: Session = Depends(get_db)):
    patient = patient_service.get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return {"data": PatientResponse.model_validate(patient), "error": None}

@router.post("", status_code=status.HTTP_201_CREATED)
def create_new_patient(patient_in: PatientCreate, db: Session = Depends(get_db)):
    try:
        # Business logic validation: phone duplication check
        existing = patient_service.get_patient_by_phone(db, patient_in.phone_number)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Patient with phone number {patient_in.phone_number} already exists"
            )
        new_patient = patient_service.create_patient(db, patient_in)
        return {"data": PatientResponse.model_validate(new_patient), "error": None}
    except HTTPException as http_exc:
        raise http_exc
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database write failure: {str(e)}")

@router.put("/{patient_id}")
def update_existing_patient(patient_id: uuid.UUID, patient_in: PatientUpdate, db: Session = Depends(get_db)):
    try:
        updated = patient_service.update_patient(db, patient_id, patient_in)
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
        return {"data": PatientResponse.model_validate(updated), "error": None}
    except HTTPException as http_exc:
        raise http_exc
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database update failure: {str(e)}")

@router.delete("/{patient_id}")
def delete_patient(patient_id: uuid.UUID, db: Session = Depends(get_db)):
    deleted = patient_service.soft_delete_patient(db, patient_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return {"data": {"success": True, "patient_id": str(patient_id)}, "error": None}

@router.get("/{patient_id}/transcripts")
def read_patient_transcripts(patient_id: uuid.UUID, db: Session = Depends(get_db)):
    # Verify patient exists first
    patient = patient_service.get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    transcripts = patient_service.get_transcripts_by_patient_id(db, patient_id)
    data = [CallTranscriptResponse.model_validate(t) for t in transcripts]
    return {"data": data, "error": None}
