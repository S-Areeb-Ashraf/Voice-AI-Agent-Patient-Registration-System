"""Utilities to extract the turn-by-turn conversation script from a Vapi
end-of-call-report webhook payload.

Every returned turn is a dict:
    {"speaker": "AI" | "Patient" | "System", "message_text": str}
ordered by conversation order.

Two strategies:
1. Preferred — Vapi sends `message.messages`: a list of per-turn objects
   ({"role": "assistant"|"user"|"system", "message"/"content": ...}).
2. Fallback — Vapi sends only the combined text transcript, where each line
   looks like "AI: Hello there" / "Caller: Hi". Those lines are split into
   speaker/text pairs.
"""
from typing import Any, Dict, List, Optional

SPEAKER_MAP = {
    "assistant": "AI",
    "ai": "AI",
    "bot": "AI",
    "user": "Patient",
    "customer": "Patient",
    "patient": "Patient",
    "caller": "Patient",
    "system": "System",
    "tool": "System",
    "toolcalls": "System",
    "function": "System",
}

MAX_MESSAGE_LENGTH = 10000


def _speaker_from_role(role: Optional[str]) -> str:
    return SPEAKER_MAP.get(str(role or "").strip().lower(), "System")


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
                part = (item.get("text") or item.get("content") or "").strip()
                if part:
                    parts.append(part)
        text = "\n".join(parts).strip()
        return text or None
    # Any other primitive (numbers etc.)
    text = str(content).strip()
    return text or None


def _extract_text(obj: Dict[str, Any]) -> Optional[str]:
    return _content_to_text(obj.get("message")) or _content_to_text(obj.get("content"))


def parse_vapi_conversation(
    messages: Optional[List[Dict[str, Any]]],
    transcript: Optional[str] = None,
) -> List[Dict[str, str]]:
    """Build the ordered turns list for storage."""
    turns: List[Dict[str, str]] = []

    # ---- Strategy 1: structured per-turn messages ----
    if isinstance(messages, list):
        for item in messages:
            if not isinstance(item, dict):
                continue
            text = _extract_text(item)
            if not text:
                continue
            # Skip tool-call placeholder turns with no spoken content.
            role = str(item.get("role") or "").strip().lower()
            speaker = _speaker_from_role(role)
            if speaker == "System" and role not in ("system",):
                # e.g. 'toolCalls' entries — not real speech
                continue
            turns.append({"speaker": speaker, "message_text": text[:MAX_MESSAGE_LENGTH]})

    # ---- Strategy 2: fall back to the combined text transcript ----
    if not turns and isinstance(transcript, str) and transcript.strip():
        current_speaker: Optional[str] = None
        for raw_line in transcript.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            speaker: Optional[str] = None
            text: Optional[str] = None
            if ":" in line:
                prefix, rest = line.split(":", 1)
                mapped = _speaker_from_role(prefix)
                rest = rest.strip()
                if rest and mapped:
                    speaker = mapped
                    text = rest
            if speaker is None:
                speaker = current_speaker or "System"
                text = line
            current_speaker = speaker
            turns.append({"speaker": speaker, "message_text": text[:MAX_MESSAGE_LENGTH]})

    return turns


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
