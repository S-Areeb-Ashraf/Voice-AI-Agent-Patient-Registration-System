# Care Cloud Voice AI Agent — Patient Registration System

This repository contains a full-stack clinical intake system comprising a **FastAPI backend**, a **React (Vite) dashboard**, and integration endpoints for a **Vapi Voice Agent**. The voice agent acts as a phone intake receptionist, conversationally registering patients, validating information, and inserting records directly into a Supabase Postgres database.


Website: [carecloudai.vercel.app/](https://carecloudai.vercel.app/)

Phone Number: +1 (346) 359 1357

`Note: Call to an AI Agent can only be made though US Number only, International calls not allowed. (VAPI restrictions).`


---

## 🏛️ System Architecture

The following flow illustrates how data is processed in this system:



### Flow Descriptions
1. **Mid-Call Integrations**: During the telephone conversation, Vapi makes POST requests to the FastAPI route `POST /vapi-tools/handle` with specific tool arguments. FastAPI executes database queries and server validations, and returns responses. The LLM translates the JSON responses into conversational speech for the caller.
2. **Post-Call Webhook**: Once the call is completed, Vapi delivers an `end-of-call-report` webhook to `POST /vapi-webhook/events`. The server logs the payload, parses the transcript and call summary, and persists it to the `call_transcripts` table linked to the patient record.
3. **Admin Dashboard**: Clinic managers browse registered patient files using the React-Vite interface, search/filter through records, view call histories, and read conversation transcripts.

---

## 🛠️ Technology Stack & Justification

*   **FastAPI & Python 3.11+**: Provides exceptional execution speed, asynchronous request processing, automatic OpenAPI interactive documentation (`/docs`), and native compatibility with **Pydantic v2** for strict schema validations.
*   **SQLAlchemy ORM**: Used with `psycopg2` to communicate with Supabase Postgres. Ensures standard OOP database mapping, protects against SQL injection, and enables a clean transition between local SQLite mock databases (used in tests) and production PostgreSQL databases.
*   **React + Vite**: Enables an extremely fast, modular, and performant frontend development workflow.
*   **Vanilla CSS**: Used for styling the frontend. Styled with a professional, clinical healthcare palette (clinical sky blue, teal, slate panels, glassmorphism overlays, custom badges, and micro-animations) to feel premium, state-of-the-art, and clean.
*   **Vapi**: Telephony and STT/TTS gateway provider. Integrates with the Gemini LLM for conversational control.

---


## 🚀 Setup & Execution Instructions

### Prerequisites
*   Python 3.11+
*   Node.js (v18+)

### 1. Database Setup
Ensure that the Supabase PostgreSQL database tables are created using the following DDL script:

```sql
CREATE TABLE patients (
    patient_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth DATE NOT NULL,
    sex TEXT NOT NULL CHECK (sex IN ('Male','Female','Other','Decline to Answer')),
    phone_number TEXT NOT NULL,
    email TEXT,
    address_line_1 TEXT NOT NULL,
    address_line_2 TEXT,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    zip_code TEXT NOT NULL,
    insurance_provider TEXT,
    insurance_member_id TEXT,
    preferred_language TEXT NOT NULL DEFAULT 'English',
    emergency_contact_name TEXT,
    emergency_contact_phone TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

CREATE TABLE call_transcripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(patient_id),
    vapi_call_id TEXT NOT NULL,
    caller_phone_number TEXT,
    transcript TEXT,
    call_summary TEXT,
    call_status TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 2. Run the Backend Web Service
From the root of the project:

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the uvicorn development server
uvicorn app.main:app --reload --port 8000
```
The interactive Swagger API documentation will be available at `http://localhost:8000/docs`.

### 3. Run Backend Test Suite
We have built a test suite with 11 test cases validating the model validators and API endpoints. Execute:
```bash
# Install test dependencies
pip install pytest httpx

# Run tests
$env:DATABASE_URL="postgresql://test:test@localhost/test"; $env:PYTHONPATH="backend"; .\venv\Scripts\pytest backend\tests\
```

### 4. Run the React Frontend Dashboard
From the root of the project:

```bash
# Navigate to frontend
cd frontend

# Install packages
npm install

# Start Vite server
npm run dev
```
Open `http://localhost:5173` in your web browser.

---

## 🎙️ Vapi Voice AI Assistant Configuration

To hook up your Vapi phone number to this backend, create a new Assistant in the Vapi Dashboard and configure the settings as follows:

### 1. System Prompt & Conversation Flow
Set the **System Prompt** for the assistant to the following:

```text
You are "Elliot", a warm, empathetic, and professional AI Clinic Intake Coordinator at Care Cloud Clinic. Your job is to register a new patient by collecting their demographic and contact details through a natural, friendly conversation. Do not sound like a machine; behave like a helpful human secretary.

### Core Registration Protocol:
1. Greet the caller warmly and ask for their name to get started.
2. Search if the patient already exists by phone number using the `lookup_patient_by_phone` tool.
   - If the patient is found, greet them by name, say: "It looks like we already have a record for [First Name] [Last Name]. Would you like to update your information instead?" and proceed to ask if they need to update fields using `update_patient`.
3. If they are a new patient, conversationally collect the REQUIRED demographic details in a natural flow:
   - First Name & Last Name (Ask them to spell them if unusual, or confirm spellings).
   - Date of Birth (Verify it is not in the future. Expect formats like MM/DD/YYYY and translate it).
   - Sex assigned at birth (Enforce one of: Male, Female, Other, Decline to Answer. Do not read the enum aloud; ask conversationally, e.g. "What was your sex assigned at birth? If you prefer not to say, you can decline to answer.")
   - Phone Number (Should be a 10-digit number. If they give a different format, ask them to repeat the 10 digits).
   - Residential Address: Street address, City, State (2-letter abbreviation), and ZIP code.
4. Once you collect the required details, ask the caller if they would like to provide optional details:
   - "I can also collect your email address, insurance information, emergency contact details, and preferred language. Would you like to provide any of those?"
   - Collect any of these optional details if they choose to provide them.
5. Critical: Before saving, read back all the collected information and ask the caller to confirm or correct any field.
   - If they correct a field, correct your internal arguments.
6. When the caller confirms all details are correct, execute the `create_patient` tool call.
7. Relay the outcome:
   - If the tool call reports success, say: "You're all set, [First Name]. Thank you for registering!" and end the call gracefully.
   - If the tool call reports validation errors (e.g. invalid date format or wrong zip code), explain the specific field error returned by the server and ask them to clarify it. Keep re-prompting until the data is corrected; never leave them with silence.
```

### 2. MID-CALL Tools JSON Schemas for VAPI Custom Tools

Define the following three Functions/Tools in the Vapi Portal. Configure their **Server URL** to point to your hosted FastAPI endpoint: `https://your-server-url.com/vapi-tools/handle`.

#### Tool: `lookup_patient_by_phone`
```json
{
  "name": "lookup_patient_by_phone",
  "description": "Checks if a patient already exists in the database using their phone number.",
  "parameters": {
    "type": "object",
    "properties": {
      "phone_number": {
        "type": "string",
        "description": "The 10-digit U.S. phone number of the patient, e.g. 1234567890."
      }
    },
    "required": ["phone_number"]
  }
}
```

#### Tool: `create_patient`
```json
{
  "name": "create_patient",
  "description": "Registers a new patient with their full demographic and contact details.",
  "parameters": {
    "type": "object",
    "properties": {
      "first_name": { "type": "string", "description": "Patient's first name, 1-50 chars, alphabetic + hyphens + apostrophes only." },
      "last_name": { "type": "string", "description": "Patient's last name, 1-50 chars, alphabetic + hyphens + apostrophes only." },
      "date_of_birth": { "type": "string", "description": "Date of birth in YYYY-MM-DD format." },
      "sex": { "type": "string", "enum": ["Male", "Female", "Other", "Decline to Answer"], "description": "Sex assigned at birth." },
      "phone_number": { "type": "string", "description": "Patient's U.S. 10-digit phone number." },
      "email": { "type": "string", "description": "Patient's email address (optional)." },
      "address_line_1": { "type": "string", "description": "Residential street address." },
      "address_line_2": { "type": "string", "description": "Apartment, suite, unit (optional)." },
      "city": { "type": "string", "description": "City name." },
      "state": { "type": "string", "description": "2-letter U.S. state abbreviation (e.g. CA)." },
      "zip_code": { "type": "string", "description": "5-digit ZIP code or ZIP+4." },
      "insurance_provider": { "type": "string", "description": "Insurance provider name (optional)." },
      "insurance_member_id": { "type": "string", "description": "Insurance member ID (optional)." },
      "preferred_language": { "type": "string", "default": "English", "description": "Preferred language (optional)." },
      "emergency_contact_name": { "type": "string", "description": "Emergency contact full name (optional)." },
      "emergency_contact_phone": { "type": "string", "description": "Emergency contact 10-digit U.S. phone number (optional)." }
    },
    "required": [
      "first_name",
      "last_name",
      "date_of_birth",
      "sex",
      "phone_number",
      "address_line_1",
      "city",
      "state",
      "zip_code"
    ]
  }
}
```

#### Tool: `update_patient`
```json
{
  "name": "update_patient",
  "description": "Updates an existing patient's details in the database.",
  "parameters": {
    "type": "object",
    "properties": {
      "patient_id": { "type": "string", "description": "The unique UUID of the patient record to update." },
      "first_name": { "type": "string", "description": "Patient's first name." },
      "last_name": { "type": "string", "description": "Patient's last name." },
      "date_of_birth": { "type": "string", "description": "Date of birth in YYYY-MM-DD format." },
      "sex": { "type": "string", "enum": ["Male", "Female", "Other", "Decline to Answer"], "description": "Sex assigned at birth." },
      "phone_number": { "type": "string", "description": "Patient's U.S. 10-digit phone number." },
      "email": { "type": "string", "description": "Patient's email address." },
      "address_line_1": { "type": "string", "description": "Residential street address." },
      "address_line_2": { "type": "string", "description": "Apartment, suite, unit." },
      "city": { "type": "string", "description": "City name." },
      "state": { "type": "string", "description": "2-letter U.S. state abbreviation." },
      "zip_code": { "type": "string", "description": "5-digit ZIP code or ZIP+4." },
      "insurance_provider": { "type": "string", "description": "Insurance provider name." },
      "insurance_member_id": { "type": "string", "description": "Insurance member ID." },
      "preferred_language": { "type": "string", "description": "Preferred language." },
      "emergency_contact_name": { "type": "string", "description": "Emergency contact full name." },
      "emergency_contact_phone": { "type": "string", "description": "Emergency contact U.S. 10-digit phone number." }
    },
    "required": ["patient_id"]
  }
}
```

### 3. Webhook Signature Configuration
1. In the Vapi Dashboard, configure the **Server URL** in the Assistant's main settings to point to your hosted endpoint: `https://your-server-url.com/vapi-webhook/events`.
2. Generate a webhook secret string. Place it in the Vapi Assistant settings as the Webhook Secret key, and configure the `VAPI_WEBHOOK_SECRET` environment variable on your FastAPI server to match it exactly.

---

## ⚖️ Trade-offs & Known Limitations

1.  **Direct Database Connection Pools vs. Session Poolers**: We have configured basic SQLAlchemy connection pooling (`pool_pre_ping=True`, `pool_size=10`). For production cloud instances with thousands of concurrent voice calls, utilizing a transaction/session pooler (such as Supabase's PgBouncer or Supabase Pooling) with smaller pool sizes on the server is highly recommended to prevent database connection exhaustion.
2.  **Telemetry Data Cache**: Currently, patient search queries fetch directly from the database with case-insensitive `ilike` filters. In a large database, searching on text columns without indices could slow queries down. Creating indexes on `phone_number` and `last_name` in PostgreSQL is recommended.
3.  **Strict Names Regex**: The validation regex (`^[A-Za-z'-]+$`) does not allow spaces in names (e.g. "Jean Paul"). This matches the take-home assessment guidelines strictly, but in a production clinical intake system, the regex should be relaxed to support double names with spaces, such as `^[A-Za-z'-]+( [A-Za-z'-]+)*$`.

---

## 🔮 Next Steps

1.  **Recording Audio Access**: Integrate Vapi's audio recording URL (which is provided in the `end-of-call-report` webhook payload) into the React dashboard so administrators can play call recordings directly.
2.  **Appointment Scheduling**: Expose a mock or real clinic schedule booking endpoint that the voice agent can trigger once registration is completed ("Would you like to schedule your first appointment for next Tuesday at 10 AM?").
3.  **HIPAA Compliance**: For production deployment, implement HIPAA-compliant end-to-end data encryption, audit trails, and store data in HIPAA-compliant BAA-covered databases (Supabase offers HIPAA-compliant plans).
