import json
import uuid
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.services import patient_service
from app.utils.logging_config import logger

router = APIRouter(prefix="/vapi-webhook", tags=["vapi"])

@router.post("/events")
async def handle_vapi_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_vapi_secret: str = Header(None, alias="x-vapi-secret")
):
    """
    Vapi Call Lifecycle Webhook.
    Verifies signature using x-vapi-secret header.
    Processes 'end-of-call-report' events, logs the full payload to stdout,
    and inserts transcripts/summaries linked to the patient's record.
    """
    # 1. Signature check (optional check based on env presence for easy local development)
    if settings.VAPI_WEBHOOK_SECRET:
        if not x_vapi_secret or x_vapi_secret != settings.VAPI_WEBHOOK_SECRET:
            logger.warning("Rejected unauthorized webhook access attempt: X-Vapi-Secret header mismatch.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized: Invalid X-Vapi-Secret signature header."
            )

    # 2. Parse payload
    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"Could not decode webhook JSON body: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed JSON payload."
        )

    message = payload.get("message", {})
    message_type = message.get("type")

    logger.info(f"Processing webhook message type: {message_type}")

    if message_type == "end-of-call-report":
        # Observability requirement: Log the full payload to stdout
        print("\n=== VAPI END-OF-CALL-REPORT FULL WEBHOOK PAYLOAD ===")
        print(json.dumps(payload, indent=2))
        print("=====================================================\n")
        
        # Extract variables
        call_obj = message.get("call", {})
        vapi_call_id = call_obj.get("id", "unknown_call_id")
        
        customer_obj = call_obj.get("customer", {})
        caller_phone = customer_obj.get("number")
        
        transcript = message.get("transcript")
        summary = message.get("summary")
        call_status = call_obj.get("status", "ended")

        # Retrieve patient_id from metadata or variables
        metadata = call_obj.get("metadata", {})
        patient_id_str = metadata.get("patient_id")
        
        # Check alternative locations Vapi might place metadata variables
        if not patient_id_str:
            variables = message.get("variables", {})
            patient_id_str = variables.get("patient_id")
            
        if not patient_id_str:
            # Fallback checking root fields in case caller forwarded metadata
            patient_id_str = payload.get("patient_id")

        patient_uuid = None
        if patient_id_str:
            try:
                patient_uuid = uuid.UUID(str(patient_id_str))
                logger.info(f"Found patient_id: {patient_uuid} in Vapi call metadata.")
            except Exception:
                logger.error(f"Patient_id '{patient_id_str}' in metadata is not a valid UUID.")

        # Fallback duplicate phone lookup to link transcript if patient_id was not explicitly passed
        if not patient_uuid and caller_phone:
            patient = patient_service.get_patient_by_phone(db, caller_phone)
            if patient:
                patient_uuid = patient.patient_id
                logger.info(f"Linked call transcript to patient ID {patient_uuid} using caller phone number match.")

        # Save transcript to DB
        try:
            transcript_record = patient_service.create_call_transcript(
                db=db,
                patient_id=patient_uuid,
                vapi_call_id=vapi_call_id,
                caller_phone_number=caller_phone,
                transcript=transcript,
                call_summary=summary,
                call_status=call_status
            )
            logger.info(f"Saved Call Transcript to DB: ID={transcript_record.id}")
        except Exception as e:
            logger.error(f"Database write failure while saving call transcript: {str(e)}")
            # Return 200 OK anyway to acknowledge receipt to Vapi server, preventing infinite retries

    return {"status": "success"}
