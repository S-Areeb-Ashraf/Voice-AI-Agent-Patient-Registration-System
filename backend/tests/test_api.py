import pytest
import json
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app import models


import os

# Setup local file-based SQLite engine for tests to allow session sharing
SQLALCHEMY_DATABASE_URL = "sqlite:///test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency override
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Apply the override to the FastAPI application dependency
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def run_around_tests():
    """Fixture to automatically create/drop table definitions and delete the file test.db."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test.db"):
        try:
            os.remove("test.db")
        except Exception:
            pass


client = TestClient(app)

def test_read_empty_patients():
    response = client.get("/patients")
    assert response.status_code == 200
    assert response.json() == {"data": [], "error": None}

def test_create_and_get_patient():
    patient_payload = {
        "first_name": "Jane",
        "last_name": "Doe",
        "date_of_birth": "1995-05-15",
        "sex": "Female",
        "phone_number": "1234567890",
        "address_line_1": "123 Main St",
        "city": "Beverly Hills",
        "state": "CA",
        "zip_code": "90210",
        "email": "jane@example.com"
    }
    
    # 1. Test POST creation
    response = client.post("/patients", json=patient_payload)
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["error"] is None
    patient_id = json_data["data"]["patient_id"]
    assert json_data["data"]["first_name"] == "Jane"
    
    # 2. Test GET by ID
    response = client.get(f"/patients/{patient_id}")
    assert response.status_code == 200
    get_json = response.json()
    assert get_json["error"] is None
    assert get_json["data"]["last_name"] == "Doe"
    
    # 3. Test duplicate phone check (should reject with 400 Bad Request)
    response = client.post("/patients", json=patient_payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["error"]

def test_validation_errors():
    # 1. Invalid phone number (non 10-digit)
    bad_payload = {
        "first_name": "Jane",
        "last_name": "Doe",
        "date_of_birth": "1995-05-15",
        "sex": "Female",
        "phone_number": "123",  # Invalid
        "address_line_1": "123 Main St",
        "city": "Beverly Hills",
        "state": "CA",
        "zip_code": "90210"
    }
    response = client.post("/patients", json=bad_payload)
    assert response.status_code == 422
    assert "phone_number" in response.json()["error"]

    # 2. Future date of birth
    bad_payload2 = {
        "first_name": "Jane",
        "last_name": "Doe",
        "date_of_birth": "3000-01-01",  # Future
        "sex": "Female",
        "phone_number": "1234567890",
        "address_line_1": "123 Main St",
        "city": "Beverly Hills",
        "state": "CA",
        "zip_code": "90210"
    }
    response = client.post("/patients", json=bad_payload2)
    assert response.status_code == 422
    assert "date_of_birth" in response.json()["error"]

def test_vapi_tools_lookup_and_create():
    # 1. Search for phone that doesn't exist
    lookup_payload = {
        "message": {
            "type": "tool-calls",
            "toolCallList": [
                {
                    "id": "tc_01",
                    "name": "lookup_patient_by_phone",
                    "arguments": {
                        "phone_number": "9876543210"
                    }
                }
            ]
        }
    }
    response = client.post("/vapi-tools/handle", json=lookup_payload)
    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["toolCallId"] == "tc_01"
    parsed_res = json.loads(results[0]["result"])
    assert parsed_res["found"] is False

    # 2. Run creation tool
    create_payload = {
        "message": {
            "type": "tool-calls",
            "toolCallList": [
                {
                    "id": "tc_02",
                    "name": "create_patient",
                    "arguments": {
                        "first_name": "Bob",
                        "last_name": "Smith",
                        "date_of_birth": "1980-04-12",
                        "sex": "Male",
                        "phone_number": "9876543210",
                        "address_line_1": "456 Oak Rd",
                        "city": "Austin",
                        "state": "TX",
                        "zip_code": "78701"
                    }
                }
            ]
        }
    }
    response = client.post("/vapi-tools/handle", json=create_payload)
    assert response.status_code == 200
    results = response.json()["results"]
    assert results[0]["toolCallId"] == "tc_02"
    parsed_res = json.loads(results[0]["result"])
    assert parsed_res["success"] is True
    patient_id = parsed_res["patient_id"]

    # 3. Lookup phone number again, should find it now
    response = client.post("/vapi-tools/handle", json=lookup_payload)
    assert response.status_code == 200
    results = response.json()["results"]
    parsed_res = json.loads(results[0]["result"])
    assert parsed_res["found"] is True
    assert parsed_res["patient_id"] == patient_id
    assert parsed_res["first_name"] == "Bob"
