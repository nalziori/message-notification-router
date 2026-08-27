"""Stand-in for anthropic.Anthropic() used by the offline smoke test
(fixtures/smoke_test.py). Zero network calls, zero API key.

Not a quality test -- it always returns the fixture's own expected label, so
it proves nothing about routing accuracy. What it does exercise for real:
context assembly, JSON-schema-shaped response parsing, label/confidence
validation, AEL recording, and output.csv writing -- every code path except
the actual model call.

Decisions are looked up by the message_id embedded in the first line of
build_context_block()'s output ("Incoming message_id: ..."), the same way a
human reading the prompt would find it.
"""

import csv
import json
from pathlib import Path
from types import SimpleNamespace

LABELS_CSV = Path(__file__).resolve().parent / "expected_labels.csv"


def _load_labels() -> dict:
    with open(LABELS_CSV, newline="", encoding="utf-8") as f:
        return {r["message_id"]: r for r in csv.DictReader(f)}


def _extract_message_id(content) -> str | None:
    # router.classify_message sends a plain string; image_pipeline sends a
    # list of content blocks. Handle both so this stub isn't router-only.
    if isinstance(content, list):
        content = next((b.get("text", "") for b in content if b.get("type") == "text"), "")
    line = next((l for l in content.splitlines() if l.startswith("Incoming message_id:")), None)
    return line.split(":", 1)[1].strip() if line else None


class _FakeMessages:
    def __init__(self, labels: dict):
        self._labels = labels

    def create(self, **kwargs):
        message_id = _extract_message_id(kwargs["messages"][0]["content"])
        label = self._labels.get(message_id)
        if label is None:
            raise RuntimeError(
                f"FakeAnthropic: no fixture label for message_id={message_id!r} "
                f"-- add it to {LABELS_CSV.name} or this case shouldn't be routed offline."
            )
        payload = {
            "sender_trust": "known_neutral_or_mixed_history",
            "urgency_signal": "no_urgency_signal",
            "risk_signal": "none",
            "repetition_signal": "first_occurrence",
            "type_candidates": [{"type": label["message_type"], "likelihood": 0.9}],
            "action": label["action"],
            "message_type": label["message_type"],
            "reason": label["note"] or f"Fixture label: {label['action']}/{label['message_type']}.",
            "confidence": 0.9,
            "evidence_message_ids": [],
        }
        return SimpleNamespace(
            stop_reason="end_turn",
            content=[SimpleNamespace(type="text", text=json.dumps(payload))],
            usage=SimpleNamespace(input_tokens=0, output_tokens=0),
        )


class FakeAnthropic:
    """Drop-in for anthropic.Anthropic(). Only .messages.create() is implemented
    because that's the only method router.classify_message() calls."""

    def __init__(self, *args, **kwargs):
        self.messages = _FakeMessages(_load_labels())
