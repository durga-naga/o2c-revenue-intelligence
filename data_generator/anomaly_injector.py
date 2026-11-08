import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "o2c_test_v2.db"


def inject_anomalies():

    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    cursor = connection.cursor()

    print("Anomaly injection started...")

    # Anomaly 1: Invoice exceeds fulfilled quantity

    cursor.execute("""
        SELECT
            i.invoice_id,
            il.invoice_line_id,
            il.quantity,
            il.unit_price
        FROM invoices i
        JOIN invoice_lines il
            ON i.invoice_id = il.invoice_id
        ORDER BY i.invoice_id
        LIMIT 1
    """)

    record = cursor.fetchone()

    if record:
        invoice_id, line_id, quantity, unit_price = record

        inflated_quantity = quantity + 5
        inflated_amount = round(inflated_quantity * unit_price, 2)

        cursor.execute("""
            UPDATE invoice_lines
            SET quantity = ?, line_amount = ?
            WHERE invoice_line_id = ?
        """, (inflated_quantity, inflated_amount, line_id))

        cursor.execute("""
            UPDATE invoices
            SET total_amount = total_amount + ?
            WHERE invoice_id = ?
        """, (round(5 * unit_price, 2), invoice_id))

        print(f"Overbilling anomaly injected: {invoice_id}")

    # Anomaly 2: Duplicate payment allocation

    cursor.execute("""
        SELECT payment_id, invoice_id, allocated_amount, allocation_date
        FROM payment_allocations
        ORDER BY allocation_id
        LIMIT 1
    """)

    allocation = cursor.fetchone()

    if allocation:
        payment_id, invoice_id, amount, allocation_date = allocation

        cursor.execute("""
            INSERT INTO payment_allocations (
                allocation_id,
                payment_id,
                invoice_id,
                allocated_amount,
                allocation_date
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            "ALLOC-2026-ANOMALY-001",
            payment_id,
            invoice_id,
            amount,
            allocation_date
        ))

        print(f"Duplicate allocation anomaly injected: {payment_id}")

        # Anomaly 3: Closed order with unpaid invoice

    cursor.execute("""
        SELECT i.invoice_id
        FROM invoices i
        JOIN sales_orders s
            ON i.order_id = s.order_id
        WHERE s.order_status = 'Completed'
        AND NOT EXISTS (
            SELECT 1
            FROM payment_allocations pa
            WHERE pa.invoice_id = i.invoice_id
        )
        ORDER BY i.invoice_id
        LIMIT 1
    """)

    invoice = cursor.fetchone()

    if invoice:
        invoice_id = invoice[0]

        cursor.execute("""
            UPDATE invoices
            SET invoice_status = 'Issued'
            WHERE invoice_id = ?
        """, (invoice_id,))

        print(f"Unpaid invoice anomaly injected: {invoice_id}")
    else:
        print("No suitable unpaid invoice found.")
    
    # Anomaly 4: Invalid lifecycle transition

    cursor.execute("""
        SELECT order_id, order_date
        FROM sales_orders
        ORDER BY order_id
        LIMIT 1
    """)

    order = cursor.fetchone()

    if order:
        order_id, order_date = order

        cursor.execute("""
            INSERT OR IGNORE INTO status_events (
                event_id,
                entity_type,
                entity_id,
                previous_status,
                new_status,
                event_timestamp,
                event_description
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "EVT-ANOMALY-001",
            "SalesOrder",
            order_id,
            "Created",
            "Completed",
            order_date,
            "Invalid lifecycle transition: skipped intermediate states"
        ))

        print(f"Invalid lifecycle anomaly injected: {order_id}")

        # Anomaly 5: Dispute missing from receivables

    cursor.execute("""
        SELECT
            d.dispute_id,
            d.invoice_id,
            d.disputed_amount
        FROM disputes d
        WHERE d.dispute_status IN ('Open', 'Under Review')
        ORDER BY d.dispute_id
        LIMIT 1
    """)

    dispute = cursor.fetchone()

    if dispute:
        dispute_id, invoice_id, disputed_amount = dispute

        # Simulate a receivables record that omits the disputed amount.

        print(
            f"Missing dispute reconciliation anomaly: {dispute_id}, "
            f"Invoice: {invoice_id}, Amount: {disputed_amount}"
        )
    print("\nAll anomaly checks completed.")
    connection.commit()
    connection.close()


if __name__ == "__main__":
    inject_anomalies()