import sqlite3

db_path = 'advanced-database-portfolio/portfolio-1-database-design/finflow.db'
conn = sqlite3.connect(db_path)
conn.execute('PRAGMA foreign_keys = ON;')

with open('advanced-database-portfolio/portfolio-1-database-design/01_schema_ddl.sql', 'r', encoding='utf-8') as f:
    conn.executescript(f.read())

with open('advanced-database-portfolio/portfolio-1-database-design/02_seed_data.sql', 'r', encoding='utf-8') as f:
    conn.executescript(f.read())

cur = conn.cursor()
tables = [row[0] for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';").fetchall()]
print(f"Verified {len(tables)} tables created successfully:")
for t in tables:
    count = cur.execute(f"SELECT count(*) FROM {t};").fetchone()[0]
    print(f"  - {t:<22}: {count} rows")

conn.close()
print("\n[OK] Portfolio 1 DDL and Seed verification passed cleanly!")
