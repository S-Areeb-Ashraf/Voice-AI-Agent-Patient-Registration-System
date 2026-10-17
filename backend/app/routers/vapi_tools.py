import json
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ValidationError

from app.database import get_db
from app.services import patient_service
from app.schemas import PatientCreate, PatientUpdate

router = APIRouter(prefix="/vapi-tools", tags=["vapi"])

class ToolCall(BaseModel):
    id: str
    name: str
    arguments: Dict[str, Any]

class ToolMessage(BaseModel):
    type: str
    toolCallList: List[ToolCall]

class VapiToolPayload(BaseModel):
    message: ToolMessage

@router.post("/handle")
def handle_vapi_tools(payload: VapiToolPayload, db: Session = Depends(get_db)):
    """
    Vapi Mid-Call Tool Execution Handler.
    Receives list of function calls, executes them via patient_service,
    and returns a serialized JSON result string for the LLM to process.
    """
    results = []
    
    for tool_call in payload.message.toolCallList:
        tool_id = tool_call.id
        tool_name = tool_call.name
        args = tool_call.arguments
        
        result_str = ""
        
        try:
            if tool_name == "lookup_patient_by_phone":
                phone = args.get("phone_number")
                patient = patient_service.get_patient_by_phone(db, phone)
                if patient:
                    result_dict = {
                        "found": True,
                        "patient_id": str(patient.patient_id),
                        "first_name": patient.first_name,
                        "last_name": patient.last_name
                    }
                else:
                    result_dict = {"found": False}
                result_str = json.dumps(result_dict)
                
            elif tool_name == "create_patient":
                try:
                    # Clean optional fields that might come in as empty strings
                    cleaned_args = {k: v for k, v in args.items() if v is not None and v != ""}
                    patient_create = PatientCreate(**cleaned_args)
                    
                    # Business check: phone number uniqueness
                    existing = patient_service.get_patient_by_phone(db, patient_create.phone_number)
                    if existing:
                        result_dict = {
                            "success": False,
                            "error": f"A patient with phone number {patient_create.phone_number} already exists as {existing.first_name} {existing.last_name}."
                        }
                    else:
                        patient = patient_service.create_patient(db, patient_create)
                        result_dict = {
                            "success": True,
                            "patient_id": str(patient.patient_id),
                            "message": "Patient created successfully"
                        }
                except ValidationError as ve:
                    # Capture specific fields that failed validation
                    errors = []
                    for error in ve.errors():
                        loc_name = " -> ".join(str(l) for l in error['loc'])
                        msg = error['msg']
                        if msg.startswith("Value error, "):
                            msg = msg.replace("Value error, ", "", 1)
                        errors.append(f"{loc_name}: {msg}")
                    error_msg = "; ".join(errors)
                    result_dict = {"success": False, "error": f"Validation failed: {error_msg}"}
                except ValueError as ve:
                    result_dict = {"success": False, "error": str(ve)}
                except Exception as e:
                    result_dict = {"success": False, "error": f"Database write failure: {str(e)}"}
                
                result_str = json.dumps(result_dict)
                
            elif tool_name == "update_patient":
                patient_id_str = args.get("patient_id")
                if not patient_id_str:
                    result_dict = {"success": False, "error": "patient_id is required to update patient"}
                else:
                    try:
                        patient_id = uuid.UUID(patient_id_str)
                        cleaned_args = {k: v for k, v in args.items() if v is not None and v != "" and k != "patient_id"}
                        patient_update = PatientUpdate(**cleaned_args)
                        
                        updated = patient_service.update_patient(db, patient_id, patient_update)
                        if updated:
                            result_dict = {
                                "success": True,
                                "patient_id": str(updated.patient_id),
                                "message": "Patient updated successfully"
                            }
                        else:
                            result_dict = {"success": False, "error": f"No active patient found with ID {patient_id_str}"}
                    except ValidationError as ve:
                        errors = []
                        for error in ve.errors():
                            loc_name = " -> ".join(str(l) for l in error['loc'])
                            msg = error['msg']
                            if msg.startswith("Value error, "):
                                msg = msg.replace("Value error, ", "", 1)
                            errors.append(f"{loc_name}: {msg}")
                        error_msg = "; ".join(errors)
                        result_dict = {"success": False, "error": f"Validation failed: {error_msg}"}
                    except ValueError as ve:
                        result_dict = {"success": False, "error": str(ve)}
                    except Exception as e:
                        result_dict = {"success": False, "error": f"Database update failure: {str(e)}"}
                
                result_str = json.dumps(result_dict)
                
            else:
                result_str = json.dumps({"success": False, "error": f"Unknown tool name: {tool_name}"})
                
        except Exception as outer_err:
            result_str = json.dumps({"success": False, "error": f"Unexpected error during tool call processing: {str(outer_err)}"})
            
        results.append({
            "toolCallId": tool_id,
            "result": result_str
        })
        
    return {"results": results}
