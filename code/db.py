"""Load dataset/*.csv into a local SQLite database (data/processed.db).

All columns are imported as TEXT. This keeps the loader generic and avoids
type-inference bugs -- callers needing numeric comparisons use CAST(col AS
INTEGER)/CAST(col AS REAL) in their query, which SQLite handles fine even
when the column affinity is TEXT.

Re-running this is idempotent: each table is dropped and rebuilt from the
current CSV contents, so it always reflects dataset/ exactly (a read-only
source we never write back to).
"""

import csv
import sqlite3
from pathlib import Path

from config import DATASET_DIR, DB_PATH

# CSV filename (without .csv) -> primary key column(s), for indexing.
# Not enforced as a SQL PRIMARY KEY (some "ids" repeat across files with
# different roles), just indexed for fast lookups.
INDEXED_COLUMNS = {
    "messages": ["message_id", "user_id", "group_id", "business_id", "sender_user_id", "media_id"],
    "sample_messages": ["message_id", "user_id", "group_id", "business_id", "sender_user_id", "media_id"],
    "users": ["user_id"],
    "groups": ["group_id"],
    "group_members": ["group_id", "user_id"],
    "business_accounts": ["business_id"],
    "user_business_history": ["user_id", "business_id"],
    "message_history": ["message_id", "user_id", "group_id", "business_id", "sender_user_id", "media_id"],
    "message_events": ["user_id", "message_id"],
    "images": ["image_id"],
    "voice_notes": ["voice_note_id"],
    "daily_notification_summary": ["user_id", "date"],
    "output": ["message_id"],
}


def _quote_ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def load_csv_to_table(conn: sqlite3.Connection, csv_path: Path, table_name: str) -> int:
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            return 0
        cols_sql = ", ".join(f"{_quote_ident(c)} TEXT" for c in header)
        conn.execute(f"DROP TABLE IF EXISTS {_quote_ident(table_name)}")
        conn.execute(f"CREATE TABLE {_quote_ident(table_name)} ({cols_sql})")
        placeholders = ", ".join("?" for _ in header)
        insert_sql = f"INSERT INTO {_quote_ident(table_name)} VALUES ({placeholders})"
        rows = [row for row in reader]
        conn.executemany(insert_sql, rows)

    for col in INDEXED_COLUMNS.get(table_name, []):
        if col in header:
            idx_name = f"idx_{table_name}_{col}"
            conn.execute(
                f"CREATE INDEX IF NOT EXISTS {_quote_ident(idx_name)} "
                f"ON {_quote_ident(table_name)} ({_quote_ident(col)})"
            )
    return len(rows)


def build_database(dataset_dir: Path = DATASET_DIR, db_path: Path = DB_PATH) -> dict:
    """Rebuild the SQLite database from every CSV in dataset/. Returns a
    table_name -> row_count summary."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        summary = {}
        for csv_path in sorted(dataset_dir.glob("*.csv")):
            table_name = csv_path.stem
            count = load_csv_to_table(conn, csv_path, table_name)
            summary[table_name] = count
        conn.commit()
        return summary
    finally:
        conn.close()


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


if __name__ == "__main__":
    summary = build_database()
    for table, count in summary.items():
        print(f"{table}: {count} rows")
