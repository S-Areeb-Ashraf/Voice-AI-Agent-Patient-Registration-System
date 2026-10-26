"""Utilities to extract the turn-by-turn conversation script from a Vapi
end-of-call-report payload.

Every returned turn is a dict:
    {"speaker": "AI" | "Patient" | "System", "message_text": str}
ordered by conversation order.

Three strategies, tried in order:
1. Vapi `artifact.messages` / `message.messages` — a list of per-turn objects
   such as {"role": "assistant" | "user", "message": "..."} (the documented
   location for the current Vapi API, see https://docs.vapi.ai/server-url/events).
2. `artifact.transcript` / `message.transcript` — the combined text transcript
   where each line looks like "AI: Hello there" / "User: Hi".
3. A transcript passed as a list of message objects instead of a string.

`message.artifact` is the current location; the top-level keys are legacy
aliases. The webhook passes whichever it found.
"""
from typing import Any, Dict, List, Optional

SPEAKER_MAP = {
    "assistant": "AI",
    "ai": "AI",
    "bot": "AI",
    "agent": "AI",
    "user": "Patient",
    "human": "Patient",
    "customer": "Patient",
    "patient": "Patient",
    "caller": "Patient",
    "system": "System",
    "tool": "System",
    "tools": "System",
    "toolcalls": "System",
    "tool_calls": "System",
    "tool_call": "System",
    "tool_call_result": "System",
    "tool_result": "System",
    "function": "System",
}

MAX_MESSAGE_LENGTH = 10000


def _speaker_from_role(role: Optional[str]) -> str:
    key = str(role or "").strip().lower().replace(" ", "_")
    return SPEAKER_MAP.get(key, "System")


def _content_to_text(content: Any) -> Optional[str]:
    """Normalize a Vapi message content field into plain text."""
    if content is None:
        return None

    if isinstance(content, str):
        text = content.strip()
        return text or None

    if isinstance(content, list):
        # Content can arrive as a list of text parts / content blocks.
        parts: List[str] = []
        for item in content:
            if isinstance(item, str):
                part = item.strip()
                if part:
                    parts.append(part)
            elif isinstance(item, dict):
                part = str(item.get("text") or item.get("content") or "").strip()
                if part:
                    parts.append(part)
        text = "\n".join(parts).strip()
        return text or None

    if isinstance(content, dict):
        part = str(content.get("text") or content.get("content") or "").strip()
        return part or None

    # Any other primitive (numbers etc.)
    text = str(content).strip()
    return text or None


def _extract_text(obj: Dict[str, Any]) -> Optional[str]:
    """Spoken text of one message object, across Vapi/OpenAI field names."""
    return (
        _content_to_text(obj.get("message"))
        or _content_to_text(obj.get("content"))
        or _content_to_text(obj.get("text"))
    )


def _extract_role(obj: Dict[str, Any]) -> str:
    role = obj.get("role")
    if not role:
        msg_type = obj.get("type")
        # OpenAI style wraps role/name inside a nested "message" object.
        nested = obj.get("message")
        if isinstance(nested, dict):
            return str(nested.get("role") or msg_type or "")
        return str(msg_type or "")
    return str(role)


def _turns_from_structured(messages: Any) -> List[Dict[str, str]]:
    turns: List[Dict[str, str]] = []

    if isinstance(messages, dict):
        messages = [messages]
    if not isinstance(messages, list):
        return turns

    for item in messages:
        if not isinstance(item, dict):
            continue

        text = _extract_text(item)
        if not text:
            # Tool-call / tool-result entries carry no spoken text.
            continue

        role = _extract_role(item).strip().lower()
        speaker = _speaker_from_role(role)

        # Only allow real speech turns; anything else (e.g. 'tool_calls')
        # is dropped rather than stored as a bogus line.
        if speaker == "System" and role not in ("system",):
            continue

        turns.append({"speaker": speaker, "message_text": text[:MAX_MESSAGE_LENGTH]})

    return turns


def _turns_from_transcript_text(transcript: str) -> List[Dict[str, str]]:
    turns: List[Dict[str, str]] = []
    current_speaker: Optional[str] = None

    for raw_line in transcript.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        speaker: Optional[str] = None
        text: Optional[str] = None

        if ":" in line:
            prefix, rest = line.split(":", 1)
            prefix_key = prefix.strip().lower().replace(" ", "_")
            rest = rest.strip()
            # Only treat the text before ':' as a speaker if we recognize it,
            # otherwise a sentence containing a colon would lose its beginning.
            if rest and prefix_key in SPEAKER_MAP:
                speaker = SPEAKER_MAP[prefix_key]
                text = rest

        if speaker is None:
            speaker = current_speaker or "System"
            text = line

        current_speaker = speaker
        turns.append({"speaker": speaker, "message_text": text[:MAX_MESSAGE_LENGTH]})

    return turns


def parse_vapi_conversation(
    messages: Any = None,
    transcript: Any = None,
) -> List[Dict[str, str]]:
    """Build the ordered turns list for storage."""
    # ---- Strategy 1: structured per-turn messages ----
    turns = _turns_from_structured(messages)

    # ---- Strategy 2: transcript as a list of message objects ----
    if not turns and isinstance(transcript, list):
        turns = _turns_from_structured(transcript)

    # ---- Strategy 3: combined text transcript ----
    if not turns and isinstance(transcript, str) and transcript.strip():
        turns = _turns_from_transcript_text(transcript)

    return turns


def build_transcript_text(turns: List[Dict[str, str]]) -> str:
    """Recreate the raw "AI: ... / Patient: ..." transcript from turns.

    Used when Vapi sends only `artifact.messages` and no combined transcript,
    so `call_transcripts.transcript` is never stored empty.
    """
    lines = []
    for turn in turns:
        prefix = "AI" if turn["speaker"] == "AI" else turn["speaker"]
        lines.append(f"{prefix}: {turn['message_text']}")
    return "\n".join(lines)


def build_message_rows(
    transcript_id: Any,
    turns: List[Dict[str, str]],
) -> List[Dict[str, Any]]:
    """Turn the parsed conversation into dicts ready for CallMessage rows."""
    rows = []
    for index, turn in enumerate(turns):
        rows.append(
            {
                "transcript_id": transcript_id,
                "turn_index": index,
                "speaker": turn["speaker"],
                "message_text": turn["message_text"],
            }
        )
    return rows
