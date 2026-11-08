import sqlite3
import random
from pathlib import Path
from datetime import date, timedelta

from master_data import (
    RANDOM_SEED,
    INDUSTRIES,
    COUNTRIES,
    PRODUCTS
)


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "o2c_database.db"


def generate_accounts(count=500):

    rng = random.Random(RANDOM_SEED)

    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")

    accounts = []

    start_date = date(2024, 1, 1)
    end_date = date(2026, 10, 31)
    total_days = (end_date - start_date).days

    for i in range(1, count + 1):

        account_id = f"ACC-2026-{i:06d}"
        account_name = f"Customer Company {i:04d}"
        industry = rng.choice(INDUSTRIES)
        country = rng.choice(COUNTRIES)

        created_date = start_date + timedelta(
            days=rng.randint(0, total_days)
        )

        accounts.append((
            account_id,
            account_name,
            industry,
            country,
            created_date.isoformat()
        ))

    connection.executemany("""
        INSERT OR IGNORE INTO accounts
        (account_id, account_name, industry, country, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, accounts)

    connection.commit()

    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM accounts")
    total = cursor.fetchone()[0]

    connection.close()

    print(f"Accounts generated successfully!")
    print(f"Total accounts in database: {total}")


def generate_quotes(count=10000):
    rng = random.Random(RANDOM_SEED)

    print("Quote generation started...")
    statuses = (
        ["Accepted"] * 7000 +
        ["Rejected"] * 1000 +
        ["Expired"] * 1000 +
        ["Sent"] * 1000
    )

    rng.shuffle(statuses)
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    cursor = connection.cursor()
    cursor.execute("SELECT account_id FROM accounts")
    account_ids = [row[0] for row in cursor.fetchall()]
    if not account_ids:
        connection.close()
        raise ValueError("No accounts found. Generate accounts first.")
    start_date = date(2025, 1, 1)
    end_date = date(2026, 10, 31)
    total_days = (end_date - start_date).days
    quotes = []
    quote_lines = []
    for i in range(1, count + 1):

        quote_id = f"QTE-2026-{i:06d}"
        
        account_id = rng.choice(account_ids)
        quote_status = statuses[i - 1]
        quote_date = start_date + timedelta(
            days=rng.randint(0, total_days)
        )

        expiry_date = quote_date + timedelta(days=30)
        product_name = rng.choice(PRODUCTS)
        quantity = rng.randint(1, 20)
        unit_price = round(rng.uniform(10000, 80000), 2)
        total_amount = round(quantity * unit_price, 2)
        quote_line_id = f"QLN-2026-{i:06d}"

        quote_lines.append((
            quote_line_id,
            quote_id,
            product_name,
            quantity,
            unit_price,
            total_amount
        ))
        quotes.append((
            quote_id,
            account_id,
            quote_date.isoformat(),
            expiry_date.isoformat(),
            quote_status,
            total_amount,
            "INR"
        ))
    cursor.executemany("""
        INSERT OR IGNORE INTO quotes
        (quote_id, account_id, quote_date, expiry_date,
         quote_status, total_amount, currency)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, quotes)

    connection.commit()
    cursor.executemany("""
        INSERT OR IGNORE INTO quote_lines
        (quote_line_id, quote_id, product_name, quantity,
         unit_price, line_amount)
        VALUES (?, ?, ?, ?, ?, ?)
    """, quote_lines)

    connection.commit()
    cursor.execute("SELECT COUNT(*) FROM quotes")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM quote_lines")
    line_total = cursor.fetchone()[0]

    connection.close()

    print(f"Total quotes generated: {total}")
    print(f"Total quote lines generated: {line_total}")

    
def generate_sales_orders():
    rng = random.Random(RANDOM_SEED)

    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT quote_id, account_id, quote_date, total_amount
        FROM quotes
        WHERE quote_status = 'Accepted'
    """)

    accepted_quotes = cursor.fetchall()
    orders = []
    order_lines = []

    for i, quote in enumerate(accepted_quotes, start=1):

        quote_id, account_id, quote_date, total_amount = quote

        order_id = f"SO-2026-{i:06d}"

        order_date = date.fromisoformat(quote_date) + timedelta(days=1)

        order_status = rng.choice([
            "Confirmed",
            "Processing",
            "Shipped",
            "Completed"
        ])

        orders.append((
            order_id,
            quote_id,
            account_id,
            order_date.isoformat(),
            order_status,
            total_amount
        ))
        cursor.execute("""
            SELECT product_name, quantity, unit_price, line_amount
            FROM quote_lines
            WHERE quote_id = ?
        """, (quote_id,))

        quote_items = cursor.fetchall()

        for j, item in enumerate(quote_items, start=1):

            product_name, quantity, unit_price, line_amount = item

            order_line_id = f"OLN-2026-{i:06d}-{j:02d}"

            order_lines.append((
                order_line_id,
                order_id,
                product_name,
                quantity,
                unit_price,
                line_amount
            ))

    cursor.executemany("""
        INSERT OR IGNORE INTO sales_orders
        (order_id, quote_id, account_id, order_date, order_status, total_amount)
        VALUES (?, ?, ?, ?, ?, ?)
    """, orders)

    connection.commit()

    cursor.executemany("""
        INSERT OR IGNORE INTO order_lines
        (order_line_id, order_id, product_name, quantity, unit_price, line_amount)
        VALUES (?, ?, ?, ?, ?, ?)
    """, order_lines)

    connection.commit()

    cursor.execute("SELECT COUNT(*) FROM sales_orders")
    order_total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM order_lines")
    line_total = cursor.fetchone()[0]

    connection.close()

    print(f"Total sales orders generated: {order_total}")
    print(f"Total order lines generated: {line_total}")
    
    print(f"Accepted quotes found: {len(accepted_quotes)}")


def generate_shipments():
    rng = random.Random(RANDOM_SEED)

    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT order_id, order_date
        FROM sales_orders
        WHERE order_status IN ('Shipped', 'Completed')
    """)

    shipped_orders = cursor.fetchall()
    shipments = []
    shipment_lines = []

    for i, order in enumerate(shipped_orders, start=1):

        order_id, order_date = order

        shipment_id = f"SHP-2026-{i:06d}"

        shipment_date = date.fromisoformat(order_date) + timedelta(days=2)
        delivery_date = shipment_date + timedelta(days=3)

        shipment_status = rng.choice([
            "Shipped",
            "In Transit",
            "Delivered"
        ])

        tracking_number = f"TRK-2026-{i:06d}"

        shipments.append((
            shipment_id,
            order_id,
            shipment_date.isoformat(),
            delivery_date.isoformat(),
            shipment_status,
            tracking_number
        ))
        cursor.execute("""
            SELECT order_line_id, quantity
            FROM order_lines
            WHERE order_id = ?
        """, (order_id,))

        order_items = cursor.fetchall()

        for j, item in enumerate(order_items, start=1):

            order_line_id, quantity = item

            shipment_line_id = f"SLN-2026-{i:06d}-{j:02d}"

            shipment_lines.append((
                shipment_line_id,
                shipment_id,
                order_line_id,
                quantity
            ))

    cursor.executemany("""
        INSERT OR IGNORE INTO shipments
        (shipment_id, order_id, shipment_date, delivery_date,
         shipment_status, tracking_number)
        VALUES (?, ?, ?, ?, ?, ?)
    """, shipments)

    connection.commit()

    cursor.executemany("""
        INSERT OR IGNORE INTO shipment_lines
        (shipment_line_id, shipment_id, order_line_id, shipped_quantity)
        VALUES (?, ?, ?, ?)
    """, shipment_lines)

    connection.commit()

    cursor.execute("SELECT COUNT(*) FROM shipments")
    shipment_total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM shipment_lines")
    line_total = cursor.fetchone()[0]

    connection.close()

    print(f"Total shipments generated: {shipment_total}")
    print(f"Total shipment lines generated: {line_total}")
    print(f"Shipped or completed orders found: {len(shipped_orders)}")


def generate_invoices():
    rng = random.Random(RANDOM_SEED)

    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT s.order_id, s.account_id, s.order_date, s.total_amount
        FROM sales_orders s
        JOIN shipments sh ON s.order_id = sh.order_id
        WHERE sh.shipment_status = 'Delivered'
    """)

    delivered_orders = cursor.fetchall()

    print(f"Delivered orders found for invoicing: {len(delivered_orders)}")

    invoices = []
    invoice_lines = []

    for i, order in enumerate(delivered_orders, start=1):

        order_id, account_id, order_date, total_amount = order

        invoice_id = f"INV-2026-{i:06d}"

        invoice_date = date.fromisoformat(order_date) + timedelta(days=5)
        due_date = invoice_date + timedelta(days=30)

        invoice_status = "Issued"

        invoices.append((
            invoice_id,
            order_id,
            account_id,
            invoice_date.isoformat(),
            due_date.isoformat(),
            invoice_status,
            total_amount,
            "INR"
        ))
        cursor.execute("""
            SELECT order_line_id, quantity, unit_price
            FROM order_lines
            WHERE order_id = ?
        """, (order_id,))

        order_items = cursor.fetchall()

        for j, item in enumerate(order_items, start=1):

            order_line_id, quantity, unit_price = item

            invoice_line_id = f"ILN-2026-{i:06d}-{j:02d}"

            line_amount = round(quantity * unit_price, 2)

            invoice_lines.append((
                invoice_line_id,
                invoice_id,
                order_line_id,
                quantity,
                unit_price,
                line_amount
            ))

    cursor.executemany("""
        INSERT OR IGNORE INTO invoices
        (invoice_id, order_id, account_id, invoice_date, due_date,
         invoice_status, total_amount, currency)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, invoices)

    connection.commit()

    cursor.executemany("""
        INSERT OR IGNORE INTO invoice_lines
        (invoice_line_id, invoice_id, order_line_id,
         quantity, unit_price, line_amount)
        VALUES (?, ?, ?, ?, ?, ?)
    """, invoice_lines)

    connection.commit()
    cursor.execute("SELECT COUNT(*) FROM invoices")
    invoice_total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM invoice_lines")
    line_total = cursor.fetchone()[0]

    connection.close()

    print(f"Total invoices generated: {invoice_total}")
    print(f"Total invoice lines generated: {line_total}")

def generate_payments():
    rng = random.Random(RANDOM_SEED)

    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT invoice_id, account_id, invoice_date, total_amount
        FROM invoices
    """)

    invoice_records = cursor.fetchall()

    print(f"Invoices found for payment generation: {len(invoice_records)}")

    payments = []

    payment_methods = [
        "Bank Transfer",
        "UPI",
        "Credit Card",
        "Cheque"
    ]

    payment_statuses = [
        "Received",
        "Pending",
        "Failed"
    ]

    for i, invoice in enumerate(invoice_records, start=1):

        invoice_id, account_id, invoice_date, total_amount = invoice

        payment_id = f"PAY-2026-{i:06d}"

        payment_date = date.fromisoformat(invoice_date) + timedelta(
            days=rng.randint(1, 45)
        )

        payment_status = rng.choice(payment_statuses)

        payment_amount = round(
            total_amount * rng.uniform(0.3, 1.0), 2
        )

        payment_method = rng.choice(payment_methods)

        payment_reference = f"REF-2026-{i:06d}"

        payments.append((
            payment_id,
            account_id,
            payment_date.isoformat(),
            payment_amount,
            payment_method,
            payment_reference,
            payment_status,
            "INR"
        ))
    cursor.executemany("""
        INSERT OR IGNORE INTO payments (
            payment_id,
            account_id,
            payment_date,
            payment_amount,
            payment_method,
            payment_reference,
            payment_status,
            currency
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, payments)

    connection.commit()

    print(f"Total payments generated: {len(payments)}")

    connection.close()
def generate_payment_allocations():

    rng = random.Random(RANDOM_SEED)

    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT payment_id, payment_amount
        FROM payments
        WHERE payment_status = 'Received'
        ORDER BY payment_id
    """)

    payment_records = cursor.fetchall()

    print(f"Received payments found: {len(payment_records)}")

    allocations = []

    for i, payment in enumerate(payment_records, start=1):

        payment_id, payment_amount = payment

        cursor.execute("""
            SELECT invoice_id
            FROM invoices
            WHERE invoice_id NOT IN (
                SELECT invoice_id
                FROM payment_allocations
            )
            ORDER BY invoice_id
        """)

        invoice_record = cursor.fetchone()

        if invoice_record is None:
            break

        invoice_id = invoice_record[0]

        allocated_amount = round(payment_amount, 2)

        allocation_date = date.today().isoformat()

        allocations.append((
            f"ALLOC-2026-{i:06d}",
            payment_id,
            invoice_id,
            allocated_amount,
            allocation_date
        ))
    cursor.executemany("""
        INSERT OR IGNORE INTO payment_allocations (
            allocation_id,
            payment_id,
            invoice_id,
            allocated_amount,
            allocation_date
        )
        VALUES (?, ?, ?, ?, ?)
    """, allocations)

    connection.commit()

    print(f"Total payment allocations generated: {len(allocations)}")

    connection.close()


def generate_disputes():

    rng = random.Random(RANDOM_SEED)

    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT invoice_id, account_id, invoice_date, total_amount
        FROM invoices
        ORDER BY invoice_id
    """)

    invoice_records = cursor.fetchall()

    print(f"Invoices found for dispute generation: {len(invoice_records)}")
    disputes = []

    dispute_reasons = [
        "Incorrect invoice amount",
        "Damaged goods",
        "Missing items",
        "Incorrect product quantity",
        "Duplicate invoice"
    ]

    for i, invoice in enumerate(invoice_records, start=1):

        invoice_id, account_id, invoice_date, total_amount = invoice

        # Only 10% of invoices will have disputes
        if rng.random() > 0.10:
            continue

        dispute_id = f"DSP-2026-{i:06d}"

        dispute_date = date.fromisoformat(invoice_date) + timedelta(
            days=rng.randint(1, 15)
        )

        dispute_reason = rng.choice(dispute_reasons)

        disputed_amount = round(
            total_amount * rng.uniform(0.1, 0.5), 2
        )

        dispute_status = rng.choice([
            "Open",
            "Under Review",
            "Resolved"
        ])

        resolution_date = None

        if dispute_status == "Resolved":
            resolution_date = (
                dispute_date + timedelta(days=rng.randint(2, 10))
            ).isoformat()

        disputes.append((
            dispute_id,
            invoice_id,
            account_id,
            dispute_date.isoformat(),
            dispute_reason,
            disputed_amount,
            dispute_status,
            resolution_date
        ))
    cursor.executemany("""
        INSERT OR IGNORE INTO disputes (
            dispute_id,
            invoice_id,
            account_id,
            dispute_date,
            dispute_reason,
            disputed_amount,
            dispute_status,
            resolution_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, disputes)

    connection.commit()

    print(f"Total disputes generated: {len(disputes)}")

    connection.close()

def generate_status_events():

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    events = []

    print("\nGenerating status events...")
    cursor.execute("""
        SELECT quote_id, quote_date, quote_status
        FROM quotes
        ORDER BY quote_id
    """)

    quote_records = cursor.fetchall()

    event_number = 1

    for quote in quote_records:

        quote_id, quote_date, quote_status = quote

        event_date = date.fromisoformat(quote_date)

        # First transition: Draft to Sent
        events.append((
            f"EVT-2026-{event_number:06d}",
            "Quote",
            quote_id,
            "Draft",
            "Sent",
            event_date.isoformat(),
            "Quote sent to customer"
        ))

        event_number += 1

        # Second transition based on final quote status
        if quote_status != "Sent":

            events.append((
                f"EVT-2026-{event_number:06d}",
                "Quote",
                quote_id,
                "Sent",
                quote_status,
                (event_date + timedelta(days=1)).isoformat(),
                f"Quote status changed to {quote_status}"
            ))

            event_number += 1

    print(f"Quote status events prepared: {len(events)}")

    cursor.execute("""
        SELECT order_id, order_date, order_status
        FROM sales_orders
        ORDER BY order_id
    """)

    order_records = cursor.fetchall()

    order_status_flow = [
        "Confirmed",
        "Processing",
        "Shipped",
        "Completed"
    ]

    for order in order_records:

        order_id, order_date, final_status = order

        order_date = date.fromisoformat(order_date)

        final_index = order_status_flow.index(final_status)

        previous_status = "Created"

        for j in range(final_index + 1):

            new_status = order_status_flow[j]

            events.append((
                f"EVT-2026-{event_number:06d}",
                "SalesOrder",
                order_id,
                previous_status,
                new_status,
                (order_date + timedelta(days=j)).isoformat(),
                f"Order status changed to {new_status}"
            ))

            event_number += 1
            previous_status = new_status

    print(f"Total status events prepared: {len(events)}")

    cursor.executemany("""
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
    """, events)

    connection.commit()

    print(f"Total status events generated: {len(events)}")

    connection.close()


if __name__ == "__main__":
    generate_accounts()
    generate_quotes()
    generate_sales_orders()
    generate_shipments()
    generate_invoices()
    generate_payments()
    generate_payment_allocations()
    generate_disputes()
    generate_status_events()

