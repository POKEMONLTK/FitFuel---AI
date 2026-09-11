"""FitFuel AI Database Setup & Seeding CLI.

Provides programmatic and CLI utilities to:
- Initialize the relational SQLite database schema from SQL DDL.
- Populate realistic demo records (athlete profile, exercise tests, meal logs, and ML feedback).
- Audit and verify table health and row counts.
- Reset the database cleanly for testing or GitHub evaluation.
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "fitfuel.db"
SCHEMA_SQL_PATH = BASE_DIR / "database" / "schema.sql"
SEED_SQL_PATH = BASE_DIR / "database" / "seed_data.sql"


def get_connection(db_file: Path | str = DB_PATH) -> sqlite3.Connection:
    """Establish connection with foreign keys and WAL mode enabled."""
    conn = sqlite3.connect(str(db_file), timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def init_schema(db_file: Path | str = DB_PATH, reset: bool = False) -> None:
    """Initialize SQLite tables from schema.sql.

    Args:
        db_file: Path to SQLite database file.
        reset: If True, drops existing tables before re-creating schema.
    """
    conn = get_connection(db_file)
    try:
        cursor = conn.cursor()
        if reset:
            cursor.execute("PRAGMA foreign_keys = OFF;")
            tables = ["feedback", "meal_items", "meals", "exercise_sessions", "users"]
            for tbl in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {tbl};")
            cursor.execute("PRAGMA foreign_keys = ON;")
            conn.commit()

        if SCHEMA_SQL_PATH.exists():
            with open(SCHEMA_SQL_PATH, "r", encoding="utf-8") as f:
                schema_script = f.read()
            cursor.executescript(schema_script)
        else:
            # Fallback to DatabaseManager.init_db if schema.sql is missing
            from database.database import DatabaseManager
            db = DatabaseManager(db_file=db_file)
            db.init_db()
        conn.commit()
    finally:
        conn.close()


def seed_demo_data(db_file: Path | str = DB_PATH) -> None:
    """Load realistic demo workouts, meals, and feedback from seed_data.sql."""
    conn = get_connection(db_file)
    try:
        cursor = conn.cursor()
        if SEED_SQL_PATH.exists():
            with open(SEED_SQL_PATH, "r", encoding="utf-8") as f:
                seed_script = f.read()
            cursor.executescript(seed_script)
            conn.commit()
        else:
            raise FileNotFoundError(f"Seed script not found at {SEED_SQL_PATH}")
    finally:
        conn.close()


def audit_database(db_file: Path | str = DB_PATH) -> dict:
    """Audit table existence and row counts."""
    conn = get_connection(db_file)
    stats = {}
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cursor.fetchall()]
        for tbl in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
            stats[tbl] = cursor.fetchone()[0]
    finally:
        conn.close()
    return stats


def main() -> None:
    """CLI entrypoint for database management."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        description="FitFuel AI SQLite Database Setup & Seeding Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python database/seed_db.py --check          # Audit current database records
  python database/seed_db.py --demo           # Populate realistic demo records
  python database/seed_db.py --reset --demo   # Clean wipe and rebuild with demo data
        """,
    )
    parser.add_argument("--db-path", type=str, default=str(DB_PATH), help="Path to SQLite database file")
    parser.add_argument("--reset", action="store_true", help="Drop all tables and re-create schema")
    parser.add_argument("--demo", action="store_true", help="Insert demonstration workouts, meals, and feedback")
    parser.add_argument("--check", action="store_true", help="Print table counts and audit health")

    args = parser.parse_args()
    target_path = Path(args.db_path)

    print(f"[DB] Target Database: {target_path.resolve()}")

    if args.reset:
        print("[RESET] Resetting database tables...")
        init_schema(target_path, reset=True)
        print("[OK] Schema recreated successfully.")

    if not target_path.exists() or not args.reset:
        init_schema(target_path, reset=False)

    if args.demo:
        print("[SEED] Seeding realistic demonstration data...")
        seed_demo_data(target_path)
        print("[OK] Demo data seeded successfully.")

    # Audit display
    stats = audit_database(target_path)
    print("\n[AUDIT] Database Status Audit:")
    print("-" * 35)
    for tbl, count in sorted(stats.items()):
        print(f"  * {tbl.ljust(20)} : {count} rows")
    print("-" * 35)
    print("[READY] Database is ready for local execution and GitHub deployment.\n")


if __name__ == "__main__":
    main()
