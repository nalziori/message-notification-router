-- Agent Execution Ledger (AEL) schema.
--
-- Append-only decision trace for the message routing pipeline. One "cycle"
-- = one message_id going through router.classify_message():
--   Planning -> Execution -> Evidence -> Verification -> Reflection -> State
--
-- This lives in its own database (data/ael.db), separate from
-- data/processed.db. db.py drops and rebuilds processed.db from dataset/*.csv
-- on every run -- the ledger must never be touched by that, since it is the
-- audit trail of what the agent actually did, not a copy of input data.

CREATE TABLE IF NOT EXISTS ael_planning (
    plan_id           TEXT PRIMARY KEY,   -- "{message_id}:plan"
    message_id        TEXT NOT NULL,
    goal              TEXT NOT NULL,      -- e.g. "classify notify/digest/mute for this message"
    context_sources   TEXT,               -- JSON array: which pull_context() sources were non-empty
                                           -- (user/group/business/media/daily_load)
    expected_evidence TEXT,               -- JSON array: evidence types this cycle may cite
    created_at        TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ael_execution (
    exec_id       TEXT PRIMARY KEY,       -- "{message_id}:exec"
    plan_id       TEXT REFERENCES ael_planning(plan_id),
    message_id    TEXT NOT NULL,
    model         TEXT,                   -- config.ANTHROPIC_MODEL
    action        TEXT,                   -- raw model output, pre-validation
    input_tokens  INTEGER,
    output_tokens INTEGER,
    status        TEXT CHECK(status IN ('success', 'failed')),
    from_cache    INTEGER DEFAULT 0,      -- 1 if served from router.py's routing cache
    ended_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ael_evidence (
    evidence_id   TEXT PRIMARY KEY,
    exec_id       TEXT REFERENCES ael_execution(exec_id),
    message_id    TEXT NOT NULL,
    evidence_type TEXT CHECK(evidence_type IN ('history_message', 'media_analysis')),
    ref_id        TEXT NOT NULL,          -- message_history.message_id, or image/voice_note id
    detail        TEXT,                   -- short excerpt/description actually used
    collected_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ael_verification (
    verify_id      TEXT PRIMARY KEY,      -- "{message_id}:verify"
    exec_id        TEXT REFERENCES ael_execution(exec_id),
    message_id     TEXT NOT NULL,
    schema_valid   INTEGER,               -- 1/0: JSON-schema-constrained response parsed cleanly
    action_valid   INTEGER,               -- 1/0: action in {notify, digest, mute}
    evidence_valid INTEGER,               -- 1/0: every cited evidence_message_id existed in context
    confidence     REAL,
    verified_at    TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ael_reflection (
    reflect_id        TEXT PRIMARY KEY,   -- "{message_id}:reflect"
    verify_id         TEXT REFERENCES ael_verification(verify_id),
    message_id        TEXT NOT NULL,
    sender_trust      TEXT,               -- router.py internal-assessment fields, reused as-is
    urgency_signal    TEXT,
    risk_signal       TEXT,
    repetition_signal TEXT,
    type_candidates   TEXT,               -- JSON
    reason            TEXT,               -- also written to output.csv
    next_action       TEXT,               -- 'none' | 'flag_for_retry' | 'needs_manual_review'
    created_at        TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ael_state (
    state_id                   TEXT PRIMARY KEY,   -- "{message_id}:state:{processed_at}"
    message_id                 TEXT NOT NULL,
    reflect_id                 TEXT REFERENCES ael_reflection(reflect_id),
    final_action                TEXT,
    final_message_type          TEXT,
    final_confidence             REAL,
    final_evidence_message_ids  TEXT,     -- JSON array, mirrors output.csv semantics
    checkpoint_type              TEXT CHECK(checkpoint_type IN ('cycle_end', 'retry', 'manual')),
    created_at                   TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_ael_planning_message     ON ael_planning(message_id);
CREATE INDEX IF NOT EXISTS idx_ael_execution_message     ON ael_execution(message_id);
CREATE INDEX IF NOT EXISTS idx_ael_evidence_message       ON ael_evidence(message_id);
CREATE INDEX IF NOT EXISTS idx_ael_verification_message   ON ael_verification(message_id);
CREATE INDEX IF NOT EXISTS idx_ael_reflection_message     ON ael_reflection(message_id);
CREATE INDEX IF NOT EXISTS idx_ael_state_message           ON ael_state(message_id);
