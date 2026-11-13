import sqlite3
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'finflow.db')

if os.path.exists(db_path):
    try:
        os.remove(db_path)
    except Exception:
        pass

conn = sqlite3.connect(db_path)
conn.execute('PRAGMA foreign_keys = ON;')

with open(os.path.join(base_dir, '01_schema_ddl.sql'), 'r', encoding='utf-8') as f:
    conn.executescript(f.read())

with open(os.path.join(base_dir, '02_seed_data.sql'), 'r', encoding='utf-8') as f:
    conn.executescript(f.read())

cur = conn.cursor()
tables = [row[0] for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';").fetchall()]
print(f"Verified {len(tables)} tables created successfully:")
for t in tables:
    count = cur.execute(f"SELECT count(*) FROM {t};").fetchone()[0]
    print(f"  - {t:<22}: {count} rows")

conn.close()
print("\n[OK] Portfolio 1 DDL and Seed verification passed cleanly!")
