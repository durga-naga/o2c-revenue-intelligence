import sqlite3
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "o2c_database.db"
REPORT_PATH = BASE_DIR / "exports" / "receivables_report.csv"


def get_connection():
    return sqlite3.connect(DB_PATH)


def test_database_integrity():
    connection = get_connection()
    result = connection.execute("PRAGMA integrity_check").fetchone()[0]
    connection.close()
    assert result == "ok"


def test_foreign_key_integrity():
    connection = get_connection()
    errors = connection.execute("PRAGMA foreign_key_check").fetchall()
    connection.close()
    assert len(errors) == 0


def test_all_13_tables_exist():
    connection = get_connection()
    tables = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    connection.close()
    assert len(tables) == 13


def test_overbilling_anomaly():
    connection = get_connection()
    result = connection.execute("""
        SELECT quantity
        FROM invoice_lines
        WHERE invoice_id = 'INV-2026-000001'
    """).fetchone()
    connection.close()
    assert result[0] == 7


def test_duplicate_allocation_anomaly():
    connection = get_connection()
    result = connection.execute("""
        SELECT COUNT(*)
        FROM payment_allocations
        WHERE payment_id = 'PAY-2026-000002'
          AND invoice_id = 'INV-2026-000001'
    """).fetchone()[0]
    connection.close()
    assert result == 2


def test_unpaid_completed_order_anomaly():
    connection = get_connection()
    result = connection.execute("""
        SELECT COUNT(*)
        FROM invoices i
        JOIN sales_orders s ON i.order_id = s.order_id
        WHERE i.invoice_id = 'INV-2026-000003'
          AND s.order_status = 'Completed'
          AND i.total_amount > (
              SELECT COALESCE(SUM(allocated_amount), 0)
              FROM payment_allocations
              WHERE invoice_id = i.invoice_id
          )
    """).fetchone()[0]
    connection.close()
    assert result == 1


def test_invalid_lifecycle_anomaly():
    connection = get_connection()
    result = connection.execute("""
        SELECT COUNT(*)
        FROM status_events
        WHERE event_id = 'EVT-ANOMALY-001'
          AND previous_status = 'Created'
          AND new_status = 'Completed'
    """).fetchone()[0]
    connection.close()
    assert result == 1


def test_missing_dispute_reconciliation():
    connection = get_connection()
    dispute = connection.execute("""
        SELECT invoice_id, disputed_amount
        FROM disputes
        WHERE dispute_id = 'DSP-2026-000004'
    """).fetchone()
    connection.close()

    with open(REPORT_PATH, newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    report_row = next(
        row for row in rows if row["invoice_id"] == dispute[0]
    )

    assert dispute[1] > 0
    assert float(report_row["disputed_amount_in_receivables"]) == 0