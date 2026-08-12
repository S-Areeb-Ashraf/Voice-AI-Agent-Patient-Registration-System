# import json
# import uuid
# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from typing import List, Dict, Any, Optional
# from pydantic import BaseModel, ValidationError

# from app.database import get_db
# from app.services import patient_service
# from app.schemas import PatientCreate, PatientUpdate

# router = APIRouter(prefix="/vapi-tools", tags=["vapi"])

# class ToolCall(BaseModel):
#     id: str
#     name: str
#     arguments: Dict[str, Any]

# class ToolMessage(BaseModel):
#     type: str
#     toolCallList: List[ToolCall]

# class VapiToolPayload(BaseModel):
#     message: ToolMessage

# @router.post("/handle")
# def handle_vapi_tools(payload: VapiToolPayload, db: Session = Depends(get_db)):
#     """
#     Vapi Mid-Call Tool Execution Handler.
#     Receives list of function calls, executes them via patient_service,
#     and returns a serialized JSON result string for the LLM to process.
#     """
#     results = []
    
#     for tool_call in payload.message.toolCallList:
#         tool_id = tool_call.id
#         tool_name = tool_call.name
#         args = tool_call.arguments
        
#         result_str = ""
        
#         try:
#             if tool_name == "lookup_patient_by_phone":
#                 phone = args.get("phone_number")
#                 patient = patient_service.get_patient_by_phone(db, phone)
#                 if patient:
#                     result_dict = {
#                         "found": True,
#                         "patient_id": str(patient.patient_id),
#                         "first_name": patient.first_name,
#                         "last_name": patient.last_name
#                     }
#                 else:
#                     result_dict = {"found": False}
#                 result_str = json.dumps(result_dict)
                
#             elif tool_name == "create_patient":
#                 try:
#                     # Clean optional fields that might come in as empty strings
#                     cleaned_args = {k: v for k, v in args.items() if v is not None and v != ""}
#                     patient_create = PatientCreate(**cleaned_args)
                    
#                     # Business check: phone number uniqueness
#                     existing = patient_service.get_patient_by_phone(db, patient_create.phone_number)
#                     if existing:
#                         result_dict = {
#                             "success": False,
#                             "error": f"A patient with phone number {patient_create.phone_number} already exists as {existing.first_name} {existing.last_name}."
#                         }
#                     else:
#                         patient = patient_service.create_patient(db, patient_create)
#                         result_dict = {
#                             "success": True,
#                             "patient_id": str(patient.patient_id),
#                             "message": "Patient created successfully"
#                         }
#                 except ValidationError as ve:
#                     # Capture specific fields that failed validation
#                     errors = []
#                     for error in ve.errors():
#                         loc_name = " -> ".join(str(l) for l in error['loc'])
#                         msg = error['msg']
#                         if msg.startswith("Value error, "):
#                             msg = msg.replace("Value error, ", "", 1)
#                         errors.append(f"{loc_name}: {msg}")
#                     error_msg = "; ".join(errors)
#                     result_dict = {"success": False, "error": f"Validation failed: {error_msg}"}
#                 except ValueError as ve:
#                     result_dict = {"success": False, "error": str(ve)}
#                 except Exception as e:
#                     result_dict = {"success": False, "error": f"Database write failure: {str(e)}"}
                
#                 result_str = json.dumps(result_dict)
                
#             elif tool_name == "update_patient":
#                 patient_id_str = args.get("patient_id")
#                 if not patient_id_str:
#                     result_dict = {"success": False, "error": "patient_id is required to update patient"}
#                 else:
#                     try:
#                         patient_id = uuid.UUID(patient_id_str)
#                         cleaned_args = {k: v for k, v in args.items() if v is not None and v != "" and k != "patient_id"}
#                         patient_update = PatientUpdate(**cleaned_args)
                        
#                         updated = patient_service.update_patient(db, patient_id, patient_update)
#                         if updated:
#                             result_dict = {
#                                 "success": True,
#                                 "patient_id": str(updated.patient_id),
#                                 "message": "Patient updated successfully"
#                             }
#                         else:
#                             result_dict = {"success": False, "error": f"No active patient found with ID {patient_id_str}"}
#                     except ValidationError as ve:
#                         errors = []
#                         for error in ve.errors():
#                             loc_name = " -> ".join(str(l) for l in error['loc'])
#                             msg = error['msg']
#                             if msg.startswith("Value error, "):
#                                 msg = msg.replace("Value error, ", "", 1)
#                             errors.append(f"{loc_name}: {msg}")
#                         error_msg = "; ".join(errors)
#                         result_dict = {"success": False, "error": f"Validation failed: {error_msg}"}
#                     except ValueError as ve:
#                         result_dict = {"success": False, "error": str(ve)}
#                     except Exception as e:
#                         result_dict = {"success": False, "error": f"Database update failure: {str(e)}"}
                
#                 result_str = json.dumps(result_dict)
                
#             else:
#                 result_str = json.dumps({"success": False, "error": f"Unknown tool name: {tool_name}"})
                
#         except Exception as outer_err:
#             result_str = json.dumps({"success": False, "error": f"Unexpected error during tool call processing: {str(outer_err)}"})
            
#         results.append({
#             "toolCallId": tool_id,
#             "result": result_str
#         })
        
#     return {"results": results}


#  new version

import json
import uuid
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, ValidationError

from app.database import get_db
from app.services import patient_service
from app.schemas import PatientCreate, PatientUpdate


router = APIRouter(prefix="/vapi-tools", tags=["vapi"])


# ============================================================
# VAPI TOOL CALL MODELS
# ============================================================

class VapiFunction(BaseModel):
    name: str
    arguments: str


class VapiToolCall(BaseModel):
    id: str
    type: str
    function: VapiFunction


class ToolMessage(BaseModel):
    toolCalls: List[VapiToolCall]


class VapiToolPayload(BaseModel):
    message: ToolMessage


# ============================================================
# VAPI TOOL HANDLER
# ============================================================

@router.post("/handle")
def handle_vapi_tools(
    payload: VapiToolPayload,
    db: Session = Depends(get_db)
):
    """
    Handles Vapi function/tool calls.

    Expected Vapi payload:

    {
        "message": {
            "toolCalls": [
                {
                    "id": "jvyqcpnp",
                    "type": "function",
                    "function": {
                        "name": "lookup_patient_by_phone",
                        "arguments": "{\"phone_number\":\"...\"}"
                    }
                }
            ]
        }
    }

    Returns:

    {
        "results": [
            {
                "toolCallId": "...",
                "result": "..."
            }
        ]
    }
    """

    results = []

    # ========================================================
    # PROCESS EACH TOOL CALL
    # ========================================================

    for tool_call in payload.message.toolCalls:

        tool_id = tool_call.id
        tool_name = tool_call.function.name
        raw_arguments = tool_call.function.arguments

        # ----------------------------------------------------
        # Parse arguments
        # ----------------------------------------------------

        try:
            if isinstance(raw_arguments, str):
                args = json.loads(raw_arguments)
            else:
                args = raw_arguments

        except json.JSONDecodeError as e:

            results.append({
                "toolCallId": tool_id,
                "result": json.dumps({
                    "success": False,
                    "error": f"Invalid tool arguments JSON: {str(e)}"
                })
            })

            continue

        # ----------------------------------------------------
        # Make sure arguments are a dictionary
        # ----------------------------------------------------

        if not isinstance(args, dict):

            results.append({
                "toolCallId": tool_id,
                "result": json.dumps({
                    "success": False,
                    "error": "Tool arguments must be a JSON object."
                })
            })

            continue

        # ----------------------------------------------------
        # Execute tool
        # ----------------------------------------------------

        try:

            # =================================================
            # LOOKUP PATIENT BY PHONE
            # =================================================

            if tool_name == "lookup_patient_by_phone":

                phone = args.get("phone_number")

                if not phone:

                    result_dict = {
                        "success": False,
                        "error": "phone_number is required"
                    }

                else:

                    patient = patient_service.get_patient_by_phone(
                        db,
                        phone
                    )

                    if patient:

                        result_dict = {
                            "found": True,
                            "patient_id": str(patient.patient_id),
                            "first_name": patient.first_name,
                            "last_name": patient.last_name
                        }

                    else:

                        result_dict = {
                            "found": False
                        }

                result_str = json.dumps(result_dict)

            # =================================================
            # CREATE PATIENT
            # =================================================

            elif tool_name == "create_patient":

                try:

                    # Remove empty optional fields
                    cleaned_args = {
                        key: value
                        for key, value in args.items()
                        if value is not None and value != ""
                    }

                    # Validate using your existing schema
                    patient_create = PatientCreate(
                        **cleaned_args
                    )

                    # Check duplicate phone number
                    existing = patient_service.get_patient_by_phone(
                        db,
                        patient_create.phone_number
                    )

                    if existing:

                        result_dict = {
                            "success": False,
                            "error": (
                                f"A patient with phone number "
                                f"{patient_create.phone_number} "
                                f"already exists as "
                                f"{existing.first_name} "
                                f"{existing.last_name}."
                            )
                        }

                    else:

                        patient = patient_service.create_patient(
                            db,
                            patient_create
                        )

                        result_dict = {
                            "success": True,
                            "patient_id": str(
                                patient.patient_id
                            ),
                            "message": (
                                "Patient created successfully"
                            )
                        }

                except ValidationError as ve:

                    errors = []

                    for error in ve.errors():

                        loc_name = " -> ".join(
                            str(location)
                            for location in error["loc"]
                        )

                        msg = error["msg"]

                        if msg.startswith("Value error, "):
                            msg = msg.replace(
                                "Value error, ",
                                "",
                                1
                            )

                        errors.append(
                            f"{loc_name}: {msg}"
                        )

                    result_dict = {
                        "success": False,
                        "error": (
                            "Validation failed: "
                            + "; ".join(errors)
                        )
                    }

                except ValueError as ve:

                    result_dict = {
                        "success": False,
                        "error": str(ve)
                    }

                except Exception as e:

                    result_dict = {
                        "success": False,
                        "error": (
                            "Database write failure: "
                            f"{str(e)}"
                        )
                    }

                result_str = json.dumps(result_dict)

            # =================================================
            # UPDATE PATIENT
            # =================================================

            elif tool_name == "update_patient":

                patient_id_str = args.get(
                    "patient_id"
                )

                if not patient_id_str:

                    result_dict = {
                        "success": False,
                        "error": (
                            "patient_id is required "
                            "to update patient"
                        )
                    }

                else:

                    try:

                        patient_id = uuid.UUID(
                            str(patient_id_str)
                        )

                        cleaned_args = {
                            key: value
                            for key, value in args.items()
                            if (
                                value is not None
                                and value != ""
                                and key != "patient_id"
                            )
                        }

                        patient_update = PatientUpdate(
                            **cleaned_args
                        )

                        updated = (
                            patient_service.update_patient(
                                db,
                                patient_id,
                                patient_update
                            )
                        )

                        if updated:

                            result_dict = {
                                "success": True,
                                "patient_id": str(
                                    updated.patient_id
                                ),
                                "message": (
                                    "Patient updated successfully"
                                )
                            }

                        else:

                            result_dict = {
                                "success": False,
                                "error": (
                                    "No active patient found "
                                    f"with ID {patient_id_str}"
                                )
                            }

                    except ValidationError as ve:

                        errors = []

                        for error in ve.errors():

                            loc_name = " -> ".join(
                                str(location)
                                for location in error["loc"]
                            )

                            msg = error["msg"]

                            if msg.startswith(
                                "Value error, "
                            ):
                                msg = msg.replace(
                                    "Value error, ",
                                    "",
                                    1
                                )

                            errors.append(
                                f"{loc_name}: {msg}"
                            )

                        result_dict = {
                            "success": False,
                            "error": (
                                "Validation failed: "
                                + "; ".join(errors)
                            )
                        }

                    except ValueError as ve:

                        result_dict = {
                            "success": False,
                            "error": str(ve)
                        }

                    except Exception as e:

                        result_dict = {
                            "success": False,
                            "error": (
                                "Database update failure: "
                                f"{str(e)}"
                            )
                        }

                result_str = json.dumps(
                    result_dict
                )

            # =================================================
            # UNKNOWN TOOL
            # =================================================

            else:

                result_str = json.dumps({
                    "success": False,
                    "error": (
                        f"Unknown tool name: {tool_name}"
                    )
                })

        except Exception as e:

            result_str = json.dumps({
                "success": False,
                "error": (
                    "Unexpected error during tool "
                    f"execution: {str(e)}"
                )
            })

        # ----------------------------------------------------
        # Vapi tool result
        # ----------------------------------------------------

        results.append({
            "toolCallId": tool_id,
            "result": result_str
        })

    # ========================================================
    # RETURN RESULTS TO VAPI
    # ========================================================

    return {
        "results": results
    }

