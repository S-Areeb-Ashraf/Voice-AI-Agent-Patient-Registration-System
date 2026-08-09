import re
from datetime import date, datetime
from typing import Optional

def validate_name(name: str, field_name: str) -> str:
    """Validates name: 1-50 chars, alphabetic + hyphens + apostrophes."""
    if not name:
        raise ValueError(f"{field_name} is required.")
    name_str = str(name).strip()
    if not (1 <= len(name_str) <= 50):
        raise ValueError(f"{field_name} must be between 1 and 50 characters.")
    # Match letters, hyphens, and apostrophes
    if not re.match(r"^[A-Za-z'-]+$", name_str):
        raise ValueError(f"{field_name} must contain only alphabetic characters, hyphens, or apostrophes (no spaces or special chars).")
    return name_str

def validate_dob(dob_input) -> date:
    """Validates date of birth: MM/DD/YYYY or YYYY-MM-DD, not in the future."""
    if not dob_input:
        raise ValueError("date_of_birth is required.")
    
    dob_val = None
    if isinstance(dob_input, date):
        dob_val = dob_input
    elif isinstance(dob_input, str):
        dob_str = dob_input.strip()
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
            try:
                dob_val = datetime.strptime(dob_str, fmt).date()
                break
            except ValueError:
                continue
        if dob_val is None:
            raise ValueError("date_of_birth must be a valid date in YYYY-MM-DD or MM/DD/YYYY format.")
    else:
        raise ValueError("date_of_birth must be a valid date.")
        
    if dob_val > date.today():
        raise ValueError("date_of_birth cannot be in the future.")
    return dob_val

def validate_sex(sex_val: str) -> str:
    """Validates sex enum: Male, Female, Other, Decline to Answer."""
    if not sex_val:
        raise ValueError("sex is required.")
    
    valid_sexes = {'Male', 'Female', 'Other', 'Decline to Answer'}
    # Flexible mapping to normalize conversational speech inputs
    sex_map = {
        "male": "Male",
        "female": "Female",
        "other": "Other",
        "decline": "Decline to Answer",
        "decline to answer": "Decline to Answer",
        "decline_to_answer": "Decline to Answer",
        "decline to respond": "Decline to Answer",
        "decline_to_respond": "Decline to Answer"
    }
    normalized = str(sex_val).strip().lower()
    mapped = sex_map.get(normalized)
    
    # Capitalize first letter as a fallback check if it might match directly
    if not mapped:
        capitalized = normalized.capitalize()
        if capitalized in valid_sexes:
            mapped = capitalized
        else:
            # Let's try matching title case
            title_case = str(sex_val).strip().title()
            if title_case in valid_sexes:
                mapped = title_case
            else:
                mapped = str(sex_val).strip()

    if mapped not in valid_sexes:
        raise ValueError("sex must be one of: 'Male', 'Female', 'Other', or 'Decline to Answer'.")
    return mapped

def validate_phone(phone_input: Optional[str], field_name: str, required: bool = True) -> Optional[str]:
    """Validates and normalizes U.S. phone numbers to exactly 10 digits."""
    if not phone_input:
        if required:
            raise ValueError(f"{field_name} is required.")
        return None
    
    # Extract only digits
    digits = re.sub(r"\D", "", str(phone_input))
    if len(digits) != 10:
        raise ValueError(f"{field_name} must be a valid 10-digit U.S. phone number.")
    return digits

def validate_state(state_input: str) -> str:
    """Validates state abbreviation: 2-letter, case-insensitive normalized to uppercase."""
    if not state_input:
        raise ValueError("state is required.")
    
    normalized = str(state_input).strip().upper()
    if not re.match(r"^[A-Z]{2}$", normalized):
        raise ValueError("state must be a valid 2-letter U.S. state abbreviation.")
    return normalized

def validate_zip(zip_input: str) -> str:
    """Validates zip code: 5-digit or ZIP+4."""
    if not zip_input:
        raise ValueError("zip_code is required.")
    
    normalized = str(zip_input).strip()
    if not re.match(r"^\d{5}(-\d{4})?$", normalized):
        raise ValueError("zip_code must be a valid 5-digit or ZIP+4 U.S. postal code.")
    return normalized

def validate_email(email_input: Optional[str]) -> Optional[str]:
    """Validates email format if present."""
    if not email_input:
        return None
    
    normalized = str(email_input).strip()
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", normalized):
        raise ValueError("email must be a valid email address.")
    return normalized
