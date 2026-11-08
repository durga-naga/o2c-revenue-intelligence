
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "o2c_test_v2.db"


def verify_anomalies():

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    print("\n===== ANOMALY VERIFICATION =====")

        # 1. Overbilling
    cursor.execute("""
        SELECT
            il.order_line_id,
            SUM(il.quantity) AS invoiced_quantity,
            (
                SELECT COALESCE(SUM(sl.shipped_quantity), 0)
                FROM shipment_lines sl
                JOIN shipments sh
                    ON sh.shipment_id = sl.shipment_id
                WHERE sl.order_line_id = il.order_line_id
                  AND sh.shipment_status = 'Delivered'
            ) AS fulfilled_quantity
        FROM invoice_lines il
        GROUP BY il.order_line_id
        HAVING invoiced_quantity > fulfilled_quantity
    """)
    print("\n1. Overbilling:", cursor.fetchall())

    # 2. Duplicate payment allocations
    cursor.execute("""
        SELECT payment_id, invoice_id, COUNT(*)
        FROM payment_allocations
        GROUP BY payment_id, invoice_id
        HAVING COUNT(*) > 1
    """)
    print("\n2. Duplicate allocations:", cursor.fetchall())

    # 3. Completed orders with unpaid balances
    cursor.execute("""
        SELECT
            i.invoice_id,
            i.total_amount,
            COALESCE(SUM(pa.allocated_amount), 0) AS allocated_amount,
            i.total_amount - COALESCE(SUM(pa.allocated_amount), 0)
                AS outstanding_balance
        FROM invoices i
        JOIN sales_orders s ON s.order_id = i.order_id
        LEFT JOIN payment_allocations pa
            ON pa.invoice_id = i.invoice_id
        WHERE s.order_status = 'Completed'
  AND i.invoice_id = 'INV-2026-001267'
        GROUP BY i.invoice_id
        HAVING outstanding_balance > 0
        ORDER BY i.invoice_id
    """)
    print("\n3. Completed orders with unpaid balances:", cursor.fetchall())

    # 4. Invalid lifecycle transition
    cursor.execute("""
        SELECT event_id, entity_id, previous_status, new_status
        FROM status_events
        WHERE event_id = 'EVT-ANOMALY-001'
          AND previous_status = 'Created'
          AND new_status = 'Completed'
    """)
    print("\n4. Invalid lifecycle:", cursor.fetchall())

        # 5. Missing dispute from receivables report
    import csv

    report_path = BASE_DIR / "exports" / "receivables_report.csv"

    with open(report_path, "r", newline="", encoding="utf-8") as file:
        report_rows = list(csv.DictReader(file))

    reported_disputes = {
        row["invoice_id"]: float(row["disputed_amount_in_receivables"])
        for row in report_rows
    }

    cursor.execute("""
        SELECT invoice_id, disputed_amount
        FROM disputes
        WHERE dispute_id = 'DSP-2026-000001'
    """)

    dispute = cursor.fetchone()

    if dispute:
        invoice_id, expected_amount = dispute
        reported_amount = reported_disputes.get(invoice_id, 0)

        print("\n5. Missing dispute reconciliation:")
        print("Dispute ID: DSP-2026-000001")
        print("Expected amount:", expected_amount)
        print("Reported amount:", reported_amount)
        print("Anomaly detected:", reported_amount < expected_amount)

    connection.close()


if __name__ == "__main__":
    verify_anomalies()
