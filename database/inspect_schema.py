import sqlite3

connection = sqlite3.connect("o2c_database.db")
cursor = connection.cursor()

tables = cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
""").fetchall()

for table in tables:
    table_name = table[0]

    columns = cursor.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    print(f"\n{table_name}:")
    print([column[1] for column in columns])

connection.close()