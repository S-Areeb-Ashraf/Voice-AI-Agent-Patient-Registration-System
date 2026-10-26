# Care Cloud Voice AI Agent — Patient Registration System

This repository contains a full-stack clinical intake system comprising a **FastAPI backend**, a **React (Vite) dashboard**, and integration endpoints for a **Vapi Voice Agent**. The voice agent acts as a phone intake receptionist, conversationally registering patients, validating information, and inserting records directly into a Supabase Postgres database.

Number: +1 (346) 359 1357
---
`Note: Call to an AI Agent can only be made though US number. International calls not allowed.`

---

## 🏛️ System Architecture

The following flow illustrates how data is processed in this system:

```mermaid

sequenceDiagram
    autonumber
    actor Caller as Caller (Patient)
    participant Vapi as Vapi (Gemini LLM)
    participant API as FastAPI Web Service
    participant DB as Supabase Postgres

    Caller->Vapi: Dials phone number & speaks naturally
    Vapi->API: Mid-call tool lookup_patient_by_phone(phone_number)
    API->DB: Query by normalized phone number
    DB-->API: Return match status / info
    API-->Vapi: Return JSON results (read aloud by LLM)
    Note over Vapi,Caller: Conversation continues;
    LLM collects details Caller->>Vapi: Confirms information is accurate
    Vapi->>API: Mid-call tool create_patient(full_fields)
    API->>API: Run server-side regex & logic validations
    alt Validation Fails
        API-->>Vapi: Return validation error details
        Vapi->>Caller: Reports error & re-prompts for specific field
    else Validation Passes
        API->>DB: Insert patient record
        DB-->>API: Confirm save
        API-->>Vapi: Return success message & patient_id
        Vapi->>Caller: "You're all set, [First Name]!" and hangs up
    end
    Vapi->>API: Webhook: POST /vapi-webhook/events (end-of-call-report)
    API->>DB: Save transcript & call summary linked to patient_id
```

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

### Storing the Per-Turn Call Conversation Script

The voice-call conversation (AI assistant vs patient) is now stored **turn-by-turn** in addition to the combined transcript.

---

## 🚀 Setup & Execution Instructions

### Prerequisites
*   Python 3.11+
*   Node.js (v18+)
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

## 🎙️ Vapi Assistant Configuration

To hook up your Vapi phone number to this backend, create a new Assistant in the Vapi Dashboard and configure the settings as follows:

### 1. System Prompt & Conversation Flow
Set the **System Prompt** for the assistant to the following:

```text
You are "Aria", a warm, empathetic, and professional AI Clinic Intake Coordinator at Care Cloud Clinic. Your job is to register a new patient by collecting their demographic and contact details through a natural, friendly conversation. Do not sound like a machine; behave like a helpful human secretary.

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

---

## 🔮 Next Steps

1.  **Recording Audio Access**: Integrate Vapi's audio recording URL (which is provided in the `end-of-call-report` webhook payload) into the React dashboard so administrators can play call recordings directly.
2.  **Appointment Scheduling**: Expose a mock or real clinic schedule booking endpoint that the voice agent can trigger once registration is completed ("Would you like to schedule your first appointment for next Tuesday at 10 AM?").
3.  **HIPAA Compliance**: For production deployment, implement HIPAA-compliant end-to-end data encryption, audit trails, and store data in HIPAA-compliant BAA-covered databases (Supabase offers HIPAA-compliant plans).
