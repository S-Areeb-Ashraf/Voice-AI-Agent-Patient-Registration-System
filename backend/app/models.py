import uuid
from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Integer, Text, text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    sex = Column(String, nullable=False)  # Enforced check constraint in DB and pydantic schema
    phone_number = Column(String, nullable=False)
    email = Column(String, nullable=True)
    address_line_1 = Column(String, nullable=False)
    address_line_2 = Column(String, nullable=True)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    zip_code = Column(String, nullable=False)
    insurance_provider = Column(String, nullable=True)
    insurance_member_id = Column(String, nullable=True)
    preferred_language = Column(String, nullable=False, default="English", server_default="English")
    emergency_contact_name = Column(String, nullable=True)
    emergency_contact_phone = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationship to transcripts
    transcripts = relationship("CallTranscript", back_populates="patient")


class CallTranscript(Base):
    __tablename__ = "call_transcripts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.patient_id"), nullable=True)
    vapi_call_id = Column(String, nullable=False)
    caller_phone_number = Column(String, nullable=True)
    transcript = Column(String, nullable=True)
    call_summary = Column(String, nullable=True)
    call_status = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationship to patient
    patient = relationship("Patient", back_populates="transcripts")
    # Ordered per-turn conversation script (AI vs patient)
    messages = relationship(
        "CallMessage",
        back_populates="transcript",
        cascade="all, delete-orphan",
        order_by="CallMessage.turn_index",
    )


class CallMessage(Base):
    """A single spoken turn of a Vapi voice call (AI / Patient / System)."""

    __tablename__ = "call_transcript_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    transcript_id = Column(UUID(as_uuid=True), ForeignKey("call_transcripts.id", ondelete="CASCADE"), nullable=False)
    turn_index = Column(Integer, nullable=False, default=0)
    speaker = Column(String, nullable=False)  # 'AI' | 'Patient' | 'System'
    message_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationship to parent transcript
    transcript = relationship("CallTranscript", back_populates="messages")
