import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import CallTranscriptResponse, CallMessageResponse
from app.services import patient_service

router = APIRouter(prefix="/calls", tags=["calls"])


@router.get("")
def read_calls(db: Session = Depends(get_db)):
    try:
        transcripts = patient_service.get_all_transcripts(db)
        data = [CallTranscriptResponse.model_validate(t) for t in transcripts]
        return {"data": data, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}


@router.get("/{transcript_id}")
def read_call(transcript_id: uuid.UUID, db: Session = Depends(get_db)):
    t = patient_service.get_transcript_by_id(db, transcript_id)
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call transcript not found")
    return {"data": CallTranscriptResponse.model_validate(t), "error": None}


@router.get("/{transcript_id}/messages")
def read_call_messages(transcript_id: uuid.UUID, db: Session = Depends(get_db)):
    """Returns the ordered per-turn conversation script (AI vs patient) of a call."""
    t = patient_service.get_transcript_by_id(db, transcript_id)
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call transcript not found")
    # Backfills the turns from the saved raw transcript for calls that were
    # stored before the per-turn table existed (or before artifact parsing).
    messages = patient_service.ensure_call_messages(db, t)
    data = [CallMessageResponse.model_validate(m) for m in messages]
    return {"data": data, "error": None}
