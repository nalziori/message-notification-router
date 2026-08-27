"""Agent Execution Ledger (AEL) client.

Append-only decision trace for the message routing pipeline (schema in
ael_schema.sql): one "cycle" = one message_id going through
router.classify_message():

    Planning -> Execution -> Evidence -> Verification -> Reflection -> State

Writes to its own database (data/ael.db), never to data/processed.db --
db.py drops and rebuilds processed.db from dataset/*.csv on every run, and
the ledger must survive that untouched since it records what the agent did,
not a copy of input data.

Usage (call once per message, right after router.classify_message() /
router.process_message() returns):

    from ael_client import init_db, record_cycle
    init_db()
    record_cycle(message_row, ctx, record)

`ctx` is the dict returned by router.pull_context(message_row).
`record` is the dict returned by router.classify_message() / cached by
router.process_message() -- must contain status, action, message_type,
reason, confidence, evidence_message_ids, internal{...}, usage{...}.
"""

import json
import sqlite3
from pathlib import Path

import config

AEL_DB_PATH = config.DATA_DIR / "ael.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "ael_schema.sql"


def get_connection(db_path: Path = AEL_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Path = AEL_DB_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.commit()
    finally:
        conn.close()


def record_cycle(message_row: dict, ctx: dict, record: dict, conn: sqlite3.Connection | None = None) -> None:
    """Write one full Planning -> State cycle for a single classification."""
    owns_conn = conn is None
    conn = conn or get_connection()
    message_id = message_row["message_id"]

    try:
        # 1. Planning
        plan_id = f"{message_id}:plan"
        context_sources = [k for k in ("user", "group", "business", "media", "daily_load") if ctx.get(k)]
        conn.execute(
            "INSERT OR REPLACE INTO ael_planning "
            "(plan_id, message_id, goal, context_sources, expected_evidence) VALUES (?, ?, ?, ?, ?)",
            (
                plan_id, message_id, "classify notify/digest/mute for this message",
                json.dumps(context_sources), json.dumps(["history_message", "media_analysis"]),
            ),
        )

        # 2. Execution
        exec_id = f"{message_id}:exec"
        usage = record.get("usage") or {}
        conn.execute(
            "INSERT OR REPLACE INTO ael_execution "
            "(exec_id, plan_id, message_id, model, action, input_tokens, output_tokens, status, from_cache) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                exec_id, plan_id, message_id, record.get("model"), record.get("action"),
                usage.get("input_tokens"), usage.get("output_tokens"), record.get("status"),
                int(bool(record.get("from_cache"))),
            ),
        )

        # 3. Evidence
        conn.execute("DELETE FROM ael_evidence WHERE exec_id = ?", (exec_id,))
        cited = set(record.get("evidence_message_ids") or [])
        for h in ctx.get("history", []):
            if h["message_id"] in cited:
                conn.execute(
                    "INSERT INTO ael_evidence (evidence_id, exec_id, message_id, evidence_type, ref_id, detail) "
                    "VALUES (?, ?, ?, 'history_message', ?, ?)",
                    (
                        f"{message_id}:ev:{h['message_id']}", exec_id, message_id, h["message_id"],
                        (h.get("message_text") or "")[:200],
                    ),
                )
        media = ctx.get("media")
        if media:
            conn.execute(
                "INSERT INTO ael_evidence (evidence_id, exec_id, message_id, evidence_type, ref_id, detail) "
                "VALUES (?, ?, ?, 'media_analysis', ?, ?)",
                (
                    f"{message_id}:ev:media", exec_id, message_id, message_row.get("media_id", ""),
                    json.dumps(media)[:500],
                ),
            )

        # 4. Verification
        valid_evidence_ids = {h["message_id"] for h in ctx.get("history", [])}
        evidence = record.get("evidence_message_ids") or []
        verify_id = f"{message_id}:verify"
        conn.execute(
            "INSERT OR REPLACE INTO ael_verification "
            "(verify_id, exec_id, message_id, schema_valid, action_valid, evidence_valid, confidence) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                verify_id, exec_id, message_id, int(record.get("status") == "success"),
                int(record.get("action") in {"notify", "digest", "mute"}),
                int(all(e in valid_evidence_ids for e in evidence)), record.get("confidence"),
            ),
        )

        # 5. Reflection
        internal = record.get("internal") or {}
        reflect_id = f"{message_id}:reflect"
        next_action = "none" if record.get("status") == "success" else "flag_for_retry"
        conn.execute(
            "INSERT OR REPLACE INTO ael_reflection "
            "(reflect_id, verify_id, message_id, sender_trust, urgency_signal, risk_signal, "
            "repetition_signal, type_candidates, reason, next_action) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                reflect_id, verify_id, message_id, internal.get("sender_trust"), internal.get("urgency_signal"),
                internal.get("risk_signal"), internal.get("repetition_signal"),
                json.dumps(internal.get("type_candidates")), record.get("reason"), next_action,
            ),
        )

        # 6. State (compacted checkpoint)
        #
        # OR REPLACE, not a plain INSERT: state_id embeds `processed_at`, which is
        # the timestamp of the ORIGINAL classification and is replayed verbatim
        # every time a cached record is re-recorded. So a second `main.py route`
        # run -- the normal path, since routing is cache-first -- regenerates the
        # exact same state_id and a plain INSERT dies on the PRIMARY KEY
        # (UNIQUE constraint failed: ael_state.state_id). Replacing is correct
        # here rather than merely convenient: same message + same processed_at is
        # by definition the same cycle, so there is no second checkpoint to keep.
        # A genuine re-classification (`--force`) writes a new processed_at and
        # therefore still lands as its own row. See test_ael_client.py.
        state_id = f"{message_id}:state:{record.get('processed_at', '')}"
        conn.execute(
            "INSERT OR REPLACE INTO ael_state "
            "(state_id, message_id, reflect_id, final_action, final_message_type, final_confidence, "
            "final_evidence_message_ids, checkpoint_type) VALUES (?, ?, ?, ?, ?, ?, ?, 'cycle_end')",
            (
                state_id, message_id, reflect_id, record.get("action"), record.get("message_type"),
                record.get("confidence"), json.dumps(evidence),
            ),
        )

        if owns_conn:
            conn.commit()
    finally:
        if owns_conn:
            conn.close()


def get_cycle(message_id: str, conn: sqlite3.Connection | None = None) -> dict:
    """Reconstruct the full Planning -> State trace for one message_id --
    the audit-trail read path (walk this when a decision needs explaining)."""
    owns_conn = conn is None
    conn = conn or get_connection()
    try:
        def one(table, extra=""):
            row = conn.execute(f"SELECT * FROM {table} WHERE message_id = ? {extra}", (message_id,)).fetchone()
            return dict(row) if row else None

        return {
            "planning": one("ael_planning"),
            "execution": one("ael_execution"),
            "evidence": [dict(r) for r in conn.execute(
                "SELECT * FROM ael_evidence WHERE message_id = ?", (message_id,)
            ).fetchall()],
            "verification": one("ael_verification"),
            "reflection": one("ael_reflection"),
            "state": one("ael_state", "ORDER BY created_at DESC LIMIT 1"),
        }
    finally:
        if owns_conn:
            conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Initialized {AEL_DB_PATH}")
