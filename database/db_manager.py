import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "o2c_database.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"


def create_database():
    connection = sqlite3.connect(DB_PATH)

    connection.execute("PRAGMA foreign_keys = ON")

    with open(SCHEMA_PATH, "r", encoding="utf-8") as file:
        schema = file.read()

    connection.executescript(schema)

    connection.commit()
    connection.close()

    print("Database created successfully!")


def verify_tables():
    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name;
    """)

    tables = cursor.fetchall()

    print("\nTables in database:")

    for table in tables:
        print(table[0])

    print("\nTotal tables:", len(tables))

    connection.close()


def validate_database():

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("PRAGMA foreign_key_check")
    foreign_key_errors = cursor.fetchall()

    cursor.execute("PRAGMA integrity_check")
    integrity_result = cursor.fetchone()[0]

    print("\nDatabase Validation:")
    print("Foreign Key Errors:", len(foreign_key_errors))
    print("Integrity Check:", integrity_result)

    connection.close()

    
def verify_record_counts():

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    tables = [
        "accounts",
        "quotes",
        "quote_lines",
        "sales_orders",
        "order_lines",
        "shipments",
        "shipment_lines",
        "invoices",
        "invoice_lines",
        "payments",
        "payment_allocations",
        "disputes",
        "status_events"
    ]

    print("\nRecord Counts:")

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table}: {count}")

    connection.close()

if __name__ == "__main__":
    verify_tables()
    validate_database()
    verify_record_counts()