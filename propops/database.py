"""Database helpers for PropOps AI."""

from __future__ import annotations

from pathlib import Path
import sqlite3

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "sql" / "propops_schema.sql"


def get_connection(db_path: Path) -> sqlite3.Connection:
    """Return a SQLite connection with foreign keys enabled."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def initialize_database(db_path: Path, schema_path: Path | None = None) -> None:
    """Create all tables defined in the schema file."""
    schema_file = schema_path or SCHEMA_PATH
    sql = schema_file.read_text(encoding="utf-8")
    with get_connection(db_path) as conn:
        conn.executescript(sql)
        conn.commit()
