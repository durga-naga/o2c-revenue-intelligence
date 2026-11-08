
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"
TEST_DB_PATH = BASE_DIR / "o2c_test_v2.db"


def create_test_database():

    if TEST_DB_PATH.exists():
        raise FileExistsError(
            f"Test database already exists: {TEST_DB_PATH}"
        )

    connection = sqlite3.connect(TEST_DB_PATH)

    try:
        connection.execute("PRAGMA foreign_keys = ON")

        with open(SCHEMA_PATH, "r", encoding="utf-8") as file:
            schema = file.read()

        connection.executescript(schema)

        foreign_key_errors = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        integrity = connection.execute(
            "PRAGMA integrity_check"
        ).fetchone()[0]

        if foreign_key_errors or integrity != "ok":
            raise RuntimeError("Test database validation failed")

        print("Fresh test database created successfully!")
        print("Database:", TEST_DB_PATH)
        print("Integrity:", integrity)
        print("Foreign key errors:", len(foreign_key_errors))

    finally:
        connection.close()


if __name__ == "__main__":
    create_test_database()
