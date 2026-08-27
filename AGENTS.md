# AGENTS.md

HackerRank Orchestrate (August 2026) — Message Notification Router

This file is a reference for any AI coding agent working in this repo: Claude Code, OpenAI Codex CLI / Codex Cloud, Gemini CLI, Cursor, Windsurf, opencode, Aider, goose, Factory, RooCode, JetBrains Junie, GitHub Copilot, Devin, or any other AGENTS.md-aware tool.

The hackathon has concluded. The session onboarding flow and mandatory per-turn logging that previously lived in this file have been removed. What remains below is the project contract, kept for reference (dataset schema, output format, evaluation constraints).

---

## 1. What This Repo Is

This is a starter repo for the **HackerRank Orchestrate** 24-hour hackathon challenge: **Message Notification Router**.

Participants must build an AI-powered system for WhatsApp. For every incoming multimodal message in `dataset/messages.csv`, the system decides whether the message should:

- `notify`: interrupt the user now
- `digest`: wait for later
- `mute`: be suppressed as low-value, repetitive, unwanted, suspicious, or unsafe

The system should use the provided user, group, business, historical message, image, voice-note, and interaction data to make personalized routing decisions across text, image posters/screenshots, and voice notes.

The final submission must produce `output.csv` with:

```text
message_id,action,message_type,reason,confidence,evidence_message_ids
```

Read `problem_statement.md` for the full participant-facing specification.

---

## 2. Project Contract

### 2.1 Dataset Contract

Participant-facing files are inside `dataset/`.

```text
dataset/
├── messages.csv
├── output.csv
├── sample_messages.csv
├── users.csv
├── groups.csv
├── group_members.csv
├── business_accounts.csv
├── user_business_history.csv
├── message_history.csv
├── message_events.csv
├── images.csv
├── voice_notes.csv
├── daily_notification_summary.csv
└── media/
    ├── images/
    └── audio/
```

Organizer-only files, if present, live outside `dataset/` and must not be used for predictions.

### 2.2 Required Output

The solution must write `output.csv` with the exact columns below:

```text
message_id,action,message_type,reason,confidence,evidence_message_ids
```

There must be exactly one prediction row for every `message_id` in `dataset/messages.csv`.
Use `none` in `evidence_message_ids` when no useful historical evidence exists.

### 2.3 Constraints That Make The Submission Evaluable

- Be runnable from the terminal.
- Read the provided files from `dataset/`.
- Do not use organizer-only files or hardcoded labels.
- Keep behavior deterministic where possible.
- Read secrets from environment variables only.
- Include clear setup and run instructions in the submitted code package.

### 2.4 Reasonable Entry Points

There is no required language. If you use Python, `code/main.py` is a good entry point. If you use another language, document the run command clearly in your submitted README.

---

## 3. Notes

- Do not assume bash. Prefer language-native APIs when possible.
- Keep tool-specific config minimal and point back to this `AGENTS.md`.
- If a nested `AGENTS.md` exists, the closest one wins for files inside that sub-project.
