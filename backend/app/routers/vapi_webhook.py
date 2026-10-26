# import json
# import uuid
# from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
# from sqlalchemy.orm import Session

# from app.database import get_db
# # from app.database import SessionLocal ----------
# from app.config import settings
# from app.services import patient_service
# from app.utils.logging_config import logger

# router = APIRouter(prefix="/vapi-webhook", tags=["vapi"])

# @router.post("/events")
# async def handle_vapi_webhook(
#     request: Request,
#     db: Session = Depends(get_db),
#     x_vapi_secret: str = Header(None, alias="x-vapi-secret")
# ):
#     """
#     Vapi Call Lifecycle Webhook.
#     Verifies signature using x-vapi-secret header.
#     Processes 'end-of-call-report' events, logs the full payload to stdout,
#     and inserts transcripts/summaries linked to the patient's record.
#     """
#     # 1. Signature check (optional check based on env presence for easy local development)
#     if settings.VAPI_WEBHOOK_SECRET:
#         if not x_vapi_secret or x_vapi_secret != settings.VAPI_WEBHOOK_SECRET:
#             logger.warning("Rejected unauthorized webhook access attempt: X-Vapi-Secret header mismatch.")
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Unauthorized: Invalid X-Vapi-Secret signature header."
#             )

#     # 2. Parse payload
#     try:
#         payload = await request.json()
#     except Exception as e:
#         logger.error(f"Could not decode webhook JSON body: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Malformed JSON payload."
#         )

#     message = payload.get("message", {})
#     message_type = message.get("type")

#     logger.info(f"Processing webhook message type: {message_type}")

#     if message_type == "end-of-call-report":
#         # Observability requirement: Log the full payload to stdout
#         print("\n=== VAPI END-OF-CALL-REPORT FULL WEBHOOK PAYLOAD ===")
#         print(json.dumps(payload, indent=2))
#         print("=====================================================\n")
        
#         # Extract variables
#         call_obj = message.get("call", {})
#         vapi_call_id = call_obj.get("id", "unknown_call_id")
        
#         customer_obj = call_obj.get("customer", {})
#         caller_phone = customer_obj.get("number")
        
#         transcript = message.get("transcript")
#         summary = message.get("summary")
#         call_status = call_obj.get("status", "ended")

#         # Retrieve patient_id from metadata or variables
#         metadata = call_obj.get("metadata", {})
#         patient_id_str = metadata.get("patient_id")



#         # Check alternative locations Vapi might place metadata variables
#         if not patient_id_str:
#             variables = message.get("variables", {})
#             patient_id_str = variables.get("patient_id")
            
#         if not patient_id_str:
#             # Fallback checking root fields in case caller forwarded metadata
#             patient_id_str = payload.get("patient_id")

#         patient_uuid = None
#         if patient_id_str:
#             try:
#                 patient_uuid = uuid.UUID(str(patient_id_str))
#                 logger.info(f"Found patient_id: {patient_uuid} in Vapi call metadata.")
#             except Exception:
#                 logger.error(f"Patient_id '{patient_id_str}' in metadata is not a valid UUID.")

#         # Fallback duplicate phone lookup to link transcript if patient_id was not explicitly passed
#         if not patient_uuid and caller_phone:
#             patient = patient_service.get_patient_by_phone(db, caller_phone)
#             if patient:
#                 patient_uuid = patient.patient_id
#                 logger.info(f"Linked call transcript to patient ID {patient_uuid} using caller phone number match.")

#         # Save transcript to DB
#         try:
#             transcript_record = patient_service.create_call_transcript(
#                 db=db,
#                 patient_id=patient_uuid,
#                 vapi_call_id=vapi_call_id,
#                 caller_phone_number=caller_phone,
#                 transcript=transcript,
#                 call_summary=summary,
#                 call_status=call_status
#             )
#             logger.info(f"Saved Call Transcript to DB: ID={transcript_record.id}")
#         except Exception as e:
#             logger.error(f"Database write failure while saving call transcript: {str(e)}")
#             # Return 200 OK anyway to acknowledge receipt to Vapi server, preventing infinite retries

#     return {"status": "success"}






# new version

import json
import uuid

from fastapi import APIRouter, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.config import settings
from app.services import patient_service
from app.utils.conversation import (
    build_transcript_text,
    parse_vapi_conversation,
)
from app.utils.logging_config import logger


router = APIRouter(prefix="/vapi-webhook", tags=["vapi"])


@router.post("/events")
async def handle_vapi_webhook(
    request: Request,
    x_vapi_secret: str = Header(None, alias="x-vapi-secret")
):
    """
    Vapi Call Lifecycle Webhook.

    - Verifies the x-vapi-secret header when configured.
    - Quickly acknowledges all Vapi webhook events.
    - Processes end-of-call-report events and saves transcripts/summaries
      to the database.
    - Database sessions are created only when database access is required.
    """

    # ---------------------------------------------------------
    # 1. Verify Vapi webhook secret
    # ---------------------------------------------------------
    if settings.VAPI_WEBHOOK_SECRET:
        if (
            not x_vapi_secret
            or x_vapi_secret != settings.VAPI_WEBHOOK_SECRET
        ):
            logger.warning(
                "Rejected unauthorized webhook access attempt: "
                "X-Vapi-Secret header mismatch."
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized: Invalid X-Vapi-Secret signature header."
            )

    # ---------------------------------------------------------
    # 2. Parse webhook payload
    # ---------------------------------------------------------
    try:
        payload = await request.json()

    except Exception as e:
        logger.error(
            f"Could not decode webhook JSON body: {str(e)}"
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed JSON payload."
        )

    # ---------------------------------------------------------
    # 3. Extract message
    # ---------------------------------------------------------
    message = payload.get("message", {})
    message_type = message.get("type")

    logger.info(
        f"Received Vapi webhook message type: {message_type}"
    )

    # ---------------------------------------------------------
    # 4. Only process end-of-call-report
    #
    # Other events such as:
    # assistant_started
    # assistant_ended
    # status-update
    # etc.
    #
    # will reach the response immediately.
    # ---------------------------------------------------------
    if message_type != "end-of-call-report":
        return {"status": "success"}

    # ---------------------------------------------------------
    # 5. Log complete end-of-call payload
    # ---------------------------------------------------------
    print(
        "\n=== VAPI END-OF-CALL-REPORT FULL WEBHOOK PAYLOAD ==="
    )

    print(
        json.dumps(
            payload,
            indent=2
        )
    )

    print(
        "=====================================================\n"
    )

    # ---------------------------------------------------------
    # 6. Extract call information
    #
    # NOTE: the current Vapi end-of-call-report keeps the conversation
    # under `message.artifact` (artifact.messages for the per-turn script,
    # artifact.transcript for the combined text). The top-level keys are
    # legacy aliases, so both locations are read.
    # ---------------------------------------------------------
    call_obj = message.get("call", {}) or {}
    if not isinstance(call_obj, dict):
        call_obj = {}

    artifact = message.get("artifact") or {}
    if not isinstance(artifact, dict):
        artifact = {}

    call_artifact = call_obj.get("artifact") or {}
    if not isinstance(call_artifact, dict):
        call_artifact = {}

    vapi_call_id = (
        call_obj.get("id")
        or message.get("callId")
        or "unknown_call_id"
    )

    customer_obj = call_obj.get("customer", {}) or {}
    if not isinstance(customer_obj, dict):
        customer_obj = {}

    caller_phone = customer_obj.get("number") or message.get("customerNumber")

    # Combined text transcript: message → artifact → call.artifact
    transcript = (
        message.get("transcript")
        or artifact.get("transcript")
        or call_artifact.get("transcript")
    )

    # AI call summary lives on message.analysis in current payloads.
    analysis = message.get("analysis") or {}
    if not isinstance(analysis, dict):
        analysis = {}

    call_analysis = call_obj.get("analysis") or {}
    if not isinstance(call_analysis, dict):
        call_analysis = {}

    summary = (
        message.get("summary")
        or analysis.get("summary")
        or artifact.get("summary")
        or call_analysis.get("summary")
    )

    call_status = (
        call_obj.get("status")
        or message.get("endedReason")
        or "ended"
    )

    # Structured per-turn conversation script (assistant vs user).
    structured_messages = (
        message.get("messages")
        or artifact.get("messages")
        or call_artifact.get("messages")
    )

    logger.info(
        "End-of-call report received: "
        f"call={vapi_call_id}, "
        f"transcript_chars={len(transcript) if isinstance(transcript, str) else 0}, "
        "messages="
        f"{len(structured_messages) if isinstance(structured_messages, list) else 0}"
    )

    # ---------------------------------------------------------
    # 7. Retrieve patient_id from metadata
    # ---------------------------------------------------------
    metadata = call_obj.get(
        "metadata",
        {}
    )

    patient_id_str = metadata.get(
        "patient_id"
    )

    # Alternative location:
    # Vapi variables
    if not patient_id_str:
        variables = message.get(
            "variables",
            {}
        )

        patient_id_str = variables.get(
            "patient_id"
        )

    # Alternative root-level location
    if not patient_id_str:
        patient_id_str = payload.get(
            "patient_id"
        )

    # ---------------------------------------------------------
    # 8. Convert patient ID to UUID
    # ---------------------------------------------------------
    patient_uuid = None

    if patient_id_str:
        try:
            patient_uuid = uuid.UUID(
                str(patient_id_str)
            )

            logger.info(
                f"Found patient_id: {patient_uuid} "
                "in Vapi call metadata."
            )

        except Exception:
            logger.error(
                f"Patient_id '{patient_id_str}' "
                "in metadata is not a valid UUID."
            )

    # ---------------------------------------------------------
    # 9. Create DB session ONLY for end-of-call processing
    # ---------------------------------------------------------
    db: Session = SessionLocal()

    try:

        # -----------------------------------------------------
        # 10. Fallback patient lookup using caller phone
        # -----------------------------------------------------
        if not patient_uuid and caller_phone:

            patient = patient_service.get_patient_by_phone(
                db,
                caller_phone
            )

            if patient:
                patient_uuid = patient.patient_id

                logger.info(
                    "Linked call transcript to patient ID "
                    f"{patient_uuid} using caller phone number match."
                )

        # -----------------------------------------------------
        # 11. Parse the conversation script (AI vs patient)
        #
        # Parsed before the transcript is saved so the combined text can be
        # rebuilt from the turns when Vapi only sends artifact.messages.
        # -----------------------------------------------------
        turns = parse_vapi_conversation(
            structured_messages,
            transcript,
        )

        if not turns:
            logger.warning(
                "No conversation turns could be parsed for call "
                f"{vapi_call_id}. Payload keys: {list(message.keys())}"
            )

        if not transcript and turns:
            transcript = build_transcript_text(turns)
            logger.info(
                "Rebuilt the raw transcript from parsed turns for call "
                f"{vapi_call_id}"
            )

        # -----------------------------------------------------
        # 12. Save transcript to database
        # -----------------------------------------------------
        try:

            transcript_record = (
                patient_service.create_call_transcript(
                    db=db,
                    patient_id=patient_uuid,
                    vapi_call_id=vapi_call_id,
                    caller_phone_number=caller_phone,
                    transcript=transcript,
                    call_summary=summary,
                    call_status=call_status
                )
            )

            logger.info(
                "Saved Call Transcript to DB: "
                f"ID={transcript_record.id}"
            )

            # -------------------------------------------------
            # 12b. Save the per-turn conversation script
            # (AI vs patient) linked to the transcript row.
            # -------------------------------------------------
            try:
                if turns:
                    saved = patient_service.create_call_messages(
                        db=db,
                        transcript_id=transcript_record.id,
                        turns=turns,
                    )
                    logger.info(
                        "Saved call conversation script to DB: "
                        f"{len(saved)} turns for transcript "
                        f"ID={transcript_record.id}"
                    )
                else:
                    logger.warning(
                        "No conversation turns could be parsed "
                        f"for call {vapi_call_id}; nothing to store."
                    )

            except Exception as msg_err:
                db.rollback()
                logger.error(
                    "Database write failure while saving "
                    f"call conversation script: {str(msg_err)}"
                )
                # Don't fail the webhook for script storage problems.

        except Exception as e:

            # Rollback so the session stays usable for the message insert.
            db.rollback()

            logger.error(
                "Database write failure while saving "
                f"call transcript: {str(e)}"
            )

            # Don't fail the webhook.
            # Vapi should still receive 200 OK.

    finally:
        # -----------------------------------------------------
        # 12. Always close database session
        # -----------------------------------------------------
        db.close()

    # ---------------------------------------------------------
    # 13. Acknowledge Vapi
    # ---------------------------------------------------------
    return {
        "status": "success"
    }
