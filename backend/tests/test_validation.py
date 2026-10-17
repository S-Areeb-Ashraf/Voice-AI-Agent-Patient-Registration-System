import pytest
from datetime import date, timedelta
from app.utils.validators import (
    validate_name, validate_dob, validate_sex,
    validate_phone, validate_state, validate_zip, validate_email
)

def test_validate_name():
    assert validate_name("John", "first_name") == "John"
    assert validate_name("O'Connor", "last_name") == "O'Connor"
    assert validate_name("Jean-Luc", "first_name") == "Jean-Luc"
    
    with pytest.raises(ValueError):
        validate_name("", "first_name")
    with pytest.raises(ValueError):
        validate_name("a" * 51, "first_name")
    with pytest.raises(ValueError):
        validate_name("John123", "first_name")
    with pytest.raises(ValueError):
        validate_name("John Doe", "first_name")  # space not allowed by regex

def test_validate_dob():
    assert validate_dob("1990-01-01") == date(1990, 1, 1)
    assert validate_dob("05/15/1985") == date(1985, 5, 15)
    assert validate_dob(date(2000, 12, 31)) == date(2000, 12, 31)
    
    # future date must fail
    future_date = date.today() + timedelta(days=1)
    with pytest.raises(ValueError):
        validate_dob(future_date)
    with pytest.raises(ValueError):
        validate_dob(future_date.strftime("%Y-%m-%d"))
    with pytest.raises(ValueError):
        validate_dob("not-a-date")

def test_validate_sex():
    assert validate_sex("Male") == "Male"
    assert validate_sex("female") == "Female"
    assert validate_sex("decline to answer") == "Decline to Answer"
    assert validate_sex("Decline to Answer") == "Decline to Answer"
    
    with pytest.raises(ValueError):
        validate_sex("Unknown")

def test_validate_phone():
    assert validate_phone("1234567890", "phone_number") == "1234567890"
    assert validate_phone("(123) 456-7890", "phone_number") == "1234567890"
    assert validate_phone("123-456-7890", "phone_number") == "1234567890"
    
    with pytest.raises(ValueError):
        validate_phone("12345", "phone_number")
    with pytest.raises(ValueError):
        validate_phone("12345678901", "phone_number")

def test_validate_state():
    assert validate_state("CA") == "CA"
    assert validate_state("tx") == "TX"
    
    with pytest.raises(ValueError):
        validate_state("California")
    with pytest.raises(ValueError):
        validate_state("A")

def test_validate_zip():
    assert validate_zip("90210") == "90210"
    assert validate_zip("12345-6789") == "12345-6789"
    
    with pytest.raises(ValueError):
        validate_zip("1234")
    with pytest.raises(ValueError):
        validate_zip("abcde")

def test_validate_email():
    assert validate_email(None) is None
    assert validate_email("") is None
    assert validate_email("test@example.com") == "test@example.com"
    
    with pytest.raises(ValueError):
        validate_email("testexample.com")
    with pytest.raises(ValueError):
        validate_email("test@example")
