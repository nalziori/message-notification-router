"""Self-check for the AEL ledger's write path.

Run directly, no test framework needed:

    python code/test_ael_client.py

Exists because of one specific regression: `record_cycle()` is called on every
routed message including cache hits, and a cached record replays its original
`processed_at` verbatim. `ael_state.state_id` embeds that timestamp, so a
second `main.py route` run -- the normal path, since routing is cache-first --
regenerates an identical state_id. With a plain INSERT that died on the PRIMARY
KEY and took the whole run down with it. test_cache_hit_replay_does_not_crash()
is the guard.
"""

import sqlite3
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ael_client

# A minimal message row + context + classification record, shaped like what
# router.pull_context() / router.classify_message() actually produce.
MESSAGE_ROW = {"message_id": "msg_001", "user_id": "u_002", "media_id": "", "media_type": ""}
CTX = {
    "user": {"user_id": "u_002"},
    "group": None,
    "business": None,
    "media": None,
    "daily_load": {"user_id": "u_002", "date": "2026-08-01"},
    "history": [
        {"message_id": "message_0238", "message_text": "your account has been suspended, verify now"},
        {"message_id": "message_0381", "message_text": "unrelated older message"},
    ],
}
RECORD = {
    "status": "success",
    "model": "claude-sonnet-5",
    "action": "mute",
    "message_type": "scam",
    "reason": "Exact repeat of a phishing message this user already reported.",
    "confidence": 0.93,
    "evidence_message_ids": ["message_0238"],
    "internal": {
        "sender_trust": "unverified_or_new_no_relationship",
        "urgency_signal": "no_urgency_signal",
        "risk_signal": "clear_scam_pattern",
        "repetition_signal": "repeated_and_reported",
        "type_candidates": [{"type": "scam", "likelihood": 0.9}],
    },
    "usage": {"input_tokens": 1200, "output_tokens": 180},
    "processed_at": "2026-08-02T14:41:00+09:00",
}


def _fresh_db() -> Path:
    db_path = Path(tempfile.mkdtemp()) / "ael.db"
    ael_client.init_db(db_path)
    return db_path


def test_cache_hit_replay_does_not_crash():
    """Two route runs over the same message: the second serves the decision from
    cache and replays the same processed_at, so it must overwrite the existing
    state row rather than collide with it."""
    db_path = _fresh_db()
    conn = ael_client.get_connection(db_path)
    try:
        ael_client.record_cycle(MESSAGE_ROW, CTX, RECORD, conn=conn)
        ael_client.record_cycle(MESSAGE_ROW, CTX, {**RECORD, "from_cache": True}, conn=conn)
        conn.commit()
        n = conn.execute("SELECT COUNT(*) FROM ael_state WHERE message_id = 'msg_001'").fetchone()[0]
        assert n == 1, f"cache-hit replay should leave one state row, got {n}"
    finally:
        conn.close()


def test_forced_reclassification_adds_a_checkpoint():
    """--force produces a genuinely new decision with a new processed_at, which
    is a distinct cycle and must NOT overwrite the earlier checkpoint."""
    db_path = _fresh_db()
    conn = ael_client.get_connection(db_path)
    try:
        ael_client.record_cycle(MESSAGE_ROW, CTX, RECORD, conn=conn)
        later = {**RECORD, "processed_at": "2026-08-03T09:15:00+09:00", "action": "digest"}
        ael_client.record_cycle(MESSAGE_ROW, CTX, later, conn=conn)
        conn.commit()
        n = conn.execute("SELECT COUNT(*) FROM ael_state WHERE message_id = 'msg_001'").fetchone()[0]
        assert n == 2, f"a re-classification should add a second checkpoint, got {n}"
    finally:
        conn.close()


def test_cycle_reconstructs_the_full_trace():
    """The read path: every stage of Planning -> State comes back, evidence is
    limited to ids actually present in the context, and verification flags the
    decision as clean."""
    db_path = _fresh_db()
    conn = ael_client.get_connection(db_path)
    try:
        ael_client.record_cycle(MESSAGE_ROW, CTX, RECORD, conn=conn)
        conn.commit()
        cycle = ael_client.get_cycle("msg_001", conn=conn)

        for stage in ("planning", "execution", "verification", "reflection", "state"):
            assert cycle[stage] is not None, f"{stage} stage missing from the trace"

        cited = [e["ref_id"] for e in cycle["evidence"]]
        assert cited == ["message_0238"], f"expected only the cited history id, got {cited}"

        assert cycle["verification"]["evidence_valid"] == 1, "cited id was present in context, should validate"
        assert cycle["execution"]["action"] == "mute"
        assert cycle["reflection"]["risk_signal"] == "clear_scam_pattern"
        assert cycle["state"]["final_action"] == "mute"
    finally:
        conn.close()


def test_hallucinated_evidence_is_flagged_not_stored():
    """A cited id that isn't in the context must fail verification -- this is the
    ledger's whole job, so it needs to actually catch it."""
    db_path = _fresh_db()
    conn = ael_client.get_connection(db_path)
    try:
        bad = {**RECORD, "evidence_message_ids": ["message_9999"]}
        ael_client.record_cycle(MESSAGE_ROW, CTX, bad, conn=conn)
        conn.commit()
        cycle = ael_client.get_cycle("msg_001", conn=conn)
        assert cycle["verification"]["evidence_valid"] == 0, "evidence not in context should fail validation"
        assert cycle["evidence"] == [], "an id absent from context has nothing to store as evidence"
    finally:
        conn.close()


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
        print(f"  [ok] {t.__name__}")
    print(f"\n{len(tests)} passed")
