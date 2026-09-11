import sqlite3
from pathlib import Path

db_path = Path("fitfuel.db")
print(f"Checking DB: {db_path.resolve()} (Exists: {db_path.exists()})")

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall() if not row[0].startswith("sqlite_")]
print("Tables found:", tables)

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [c[1] for c in cursor.fetchall()]
    print(f"\n--- Table: {table} ({count} rows) ---")
    print("Columns:", cols)
    cursor.execute(f"SELECT * FROM {table} LIMIT 2")
    sample = [dict(r) for r in cursor.fetchall()]
    for s in sample:
        print("  Sample row:", s)
