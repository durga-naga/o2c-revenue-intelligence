import sqlite3
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "o2c_test_v2.db"
EXPORT_DIR = BASE_DIR / "exports"

EXPORT_DIR.mkdir(exist_ok=True)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

tables = conn.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
      AND name NOT LIKE 'sqlite_%'
    ORDER BY rowid
""").fetchall()

data = {}

for table in tables:
    table_name = table["name"]
    rows = conn.execute(f'SELECT * FROM "{table_name}"').fetchall()
    data[table_name] = [dict(row) for row in rows]

with open(EXPORT_DIR / "o2c_database.json", "w", encoding="utf-8") as file:
    json.dump(data, file, indent=2, ensure_ascii=False)

with open(EXPORT_DIR / "o2c_database.sql", "w", encoding="utf-8") as file:
    file.write("\n".join(conn.iterdump()))

conn.close()

print("JSON and SQL exports generated successfully.")

for table, rows in data.items():
    print(f"{table}: {len(rows)}")