import json
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.database import get_db
from app.services import patient_service
from app.schemas import PatientCreate, PatientUpdate
from app.utils.logging_config import logger
from app.utils.validators import validate_phone

router = APIRouter(prefix="/vapi-tools", tags=["vapi"])


# ===========================================================================
# Vapi tool-call payload normalization
# ===========================================================================
# Vapi has shipped more than one shape for the `tool-calls` server message.
# All of these are accepted (see https://docs.vapi.ai/server-url/events):
#
#   current — OpenAI style, name/arguments nested under "function"
#   {
#     "message": {
#       "type": "tool-calls",
#       "toolCallList": [
#         {"id": "abc", "type": "function",
#          "function": {"name": "create_patient", "arguments": {...}}}
#       ]
#     }
#   }
#
#   older / flat
#   {"message": {"toolCallList": [
#       {"id": "abc", "name": "create_patient", "arguments": {...}}]}}
#
#   toolWithToolCallList (same call, one level deeper, next to the definition)
#   {"message": {"toolWithToolCallList": [
#       {"type": "function", "function": {"name": "..."},
#        "toolCall": {"id": "abc", "function": {"name": "...", "arguments": {}}}}]}}
#
# `arguments` may arrive as a JSON object or as a JSON-encoded string.
#
# Why this is normalized by hand instead of declared as a Pydantic model:
# a 422 on this endpoint happens *during a live phone call*. The assistant
# receives "Validation failed: message -> toolCallList -> 0 -> name ..." and
# has no way to recover, which is exactly what broke real calls. Every tool
# call must therefore be answered with an HTTP 200 and a readable result
# string, whatever the payload looks like.
# ===========================================================================

TOOL_CALL_ARRAY_KEYS = ("toolCallList", "toolCalls", "toolWithToolCallList")


def _coerce_arguments(raw: Any) -> Dict[str, Any]:
    """Accept a dict, a JSON-encoded string, or nothing at all."""
    if raw is None or raw == "":
        return {}
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except (ValueError, TypeError):
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def _normalize_tool_call(item: Any) -> Optional[Dict[str, Any]]:
    """Flatten one Vapi tool call entry into {id, name, arguments}."""
    if not isinstance(item, dict):
        return None

    # `toolWithToolCallList` entries keep the actual invocation in `toolCall`.
    inner = item.get("toolCall") if isinstance(item.get("toolCall"), dict) else item
    inner_fn = inner.get("function") if isinstance(inner.get("function"), dict) else {}
    item_fn = item.get("function") if isinstance(item.get("function"), dict) else {}

    call_id = (
        inner.get("id")
        or item.get("id")
        or inner.get("toolCallId")
        or item.get("toolCallId")
        or ""
    )

    name = (
        inner.get("name")
        or inner_fn.get("name")
        or item.get("name")
        or item_fn.get("name")
        or ""
    )

    # Look for arguments on the invocation first, then on the function body.
    args_raw = inner.get("arguments")
    if args_raw is None:
        args_raw = inner_fn.get("arguments")
    if args_raw is None:
        args_raw = item.get("arguments")
    if args_raw is None:
        args_raw = item_fn.get("arguments")

    return {
        "id": str(call_id),
        "name": str(name).strip(),
        "arguments": _coerce_arguments(args_raw),
    }


def extract_tool_calls(message: Any) -> List[Dict[str, Any]]:
    """Collect every tool call in a Vapi `message`, de-duplicated by id."""
    if not isinstance(message, dict):
        return []

    calls: List[Dict[str, Any]] = []
    seen_ids = set()

    for key in TOOL_CALL_ARRAY_KEYS:
        value = message.get(key)
        if not isinstance(value, list):
            continue

        for item in value:
            call = _normalize_tool_call(item)
            if not call:
                continue

            # The same invocation is often present in both `toolCallList`
            # and `toolWithToolCallList`. Executing it twice would create
            # duplicate patient records, so drop repeats by id.
            if call["id"]:
                if call["id"] in seen_ids:
                    continue
                seen_ids.add(call["id"])

            calls.append(call)

    return calls


def _format_validation_error(ve: ValidationError) -> Dict[str, Any]:
    """Turn a Pydantic error into a message the LLM can act on."""
    errors = []
    fields: Dict[str, str] = {}
    for error in ve.errors():
        loc_name = " -> ".join(str(l) for l in error["loc"]) or "field"
        msg = error["msg"]
        if msg.startswith("Value error, "):
            msg = msg.replace("Value error, ", "", 1)
        errors.append(f"{loc_name}: {msg}")
        if not loc_name.startswith("__"):
            fields[loc_name] = msg

    return {
        "success": False,
        "error": "Validation failed: " + "; ".join(errors),
        "invalid_fields": fields,
    }


def _lookup_patient(db: Session, args: Dict[str, Any]) -> Dict[str, Any]:
    phone = args.get("phone_number") or args.get("phone") or args.get("number")

    if not phone:
        return {
            "found": False,
            "error": (
                "phone_number is required. Ask the caller for their 10-digit "
                "U.S. phone number before looking them up."
            ),
        }

    try:
        clean_phone = validate_phone(str(phone), "phone_number", required=True)
    except ValueError:
        return {
            "found": False,
            "error": (
                f"'{phone}' is not a valid 10-digit U.S. phone number. Ask the "
                "caller to repeat the 10 digits."
            ),
        }

    patient = patient_service.get_patient_by_phone(db, clean_phone)
    if not patient:
        return {"found": False}

    return {
        "found": True,
        "patient_id": str(patient.patient_id),
        "first_name": patient.first_name,
        "last_name": patient.last_name,
    }


def _create_patient(db: Session, args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Drop empty optional values, which LLMs commonly send as "".
        cleaned_args = {k: v for k, v in args.items() if v is not None and v != ""}
        patient_create = PatientCreate(**cleaned_args)

        existing = patient_service.get_patient_by_phone(db, patient_create.phone_number)
        if existing:
            return {
                "success": False,
                "error": (
                    f"A patient with phone number {patient_create.phone_number} "
                    f"already exists as {existing.first_name} {existing.last_name}."
                ),
            }

        patient = patient_service.create_patient(db, patient_create)
        return {
            "success": True,
            "patient_id": str(patient.patient_id),
            "message": "Patient created successfully",
        }

    except ValidationError as ve:
        return _format_validation_error(ve)
    except ValueError as ve:
        return {"success": False, "error": str(ve)}
    except Exception as e:
        db.rollback()
        return {"success": False, "error": f"Database write failure: {str(e)}"}


def _update_patient(db: Session, args: Dict[str, Any]) -> Dict[str, Any]:
    patient_id_str = args.get("patient_id")
    if not patient_id_str:
        return {
            "success": False,
            "error": "patient_id is required to update a patient. Look the patient up by phone first.",
        }

    try:
        patient_id = uuid.UUID(str(patient_id_str))
    except (ValueError, AttributeError, TypeError):
        return {"success": False, "error": f"'{patient_id_str}' is not a valid patient_id UUID."}

    try:
        cleaned_args = {
            k: v
            for k, v in args.items()
            if v is not None and v != "" and k != "patient_id"
        }
        patient_update = PatientUpdate(**cleaned_args)

        updated = patient_service.update_patient(db, patient_id, patient_update)
        if not updated:
            return {"success": False, "error": f"No active patient found with ID {patient_id_str}"}

        return {
            "success": True,
            "patient_id": str(updated.patient_id),
            "message": "Patient updated successfully",
        }

    except ValidationError as ve:
        return _format_validation_error(ve)
    except ValueError as ve:
        return {"success": False, "error": str(ve)}
    except Exception as e:
        db.rollback()
        return {"success": False, "error": f"Database update failure: {str(e)}"}


def _execute_tool(call: Dict[str, Any], db: Session) -> str:
    """Run one normalized tool call and return the JSON string for the LLM."""
    name = call.get("name") or ""
    args = call.get("arguments") or {}

    if not name:
        return json.dumps({
            "success": False,
            "error": "The tool call did not include a function name.",
        })

    logger.info(f"Executing Vapi tool '{name}' with arguments: {list(args.keys())}")

    try:
        if name == "lookup_patient_by_phone":
            return json.dumps(_lookup_patient(db, args))
        if name == "create_patient":
            return json.dumps(_create_patient(db, args))
        if name == "update_patient":
            return json.dumps(_update_patient(db, args))

        return json.dumps({"success": False, "error": f"Unknown tool name: {name}"})

    except Exception as outer_err:
        logger.error(f"Unexpected error in Vapi tool '{name}': {str(outer_err)}")
        return json.dumps({
            "success": False,
            "error": f"Unexpected error during tool call processing: {str(outer_err)}",
        })


@router.post("/handle")
async def handle_vapi_tools(request: Request, db: Session = Depends(get_db)):
    """
    Vapi Mid-Call Tool Execution Handler.

    Accepts any Vapi tool-call payload shape, executes each call through
    patient_service, and always answers 200 with one result string per call.
    """
    try:
        payload = await request.json()
    except Exception as exc:
        logger.error(f"Vapi tool request body was not valid JSON: {str(exc)}")
        return {"results": []}

    message = payload.get("message") if isinstance(payload, dict) else None
    if not isinstance(message, dict):
        message = payload if isinstance(payload, dict) else {}

    tool_calls = extract_tool_calls(message)

    if not tool_calls:
        logger.warning(
            "Vapi tool request contained no recognizable tool calls. "
            f"Payload keys: {list(message.keys())}"
        )

    results = [
        {
            "toolCallId": call["id"],
            "result": _execute_tool(call, db),
        }
        for call in tool_calls
    ]

    return {"results": results}
