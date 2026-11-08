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
DB_PATH = BASE_DIR / "o2c_test_v2.db"


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
        SELECT s.order_id, s.order_date,
               ol.order_line_id, ol.quantity
        FROM sales_orders s
        JOIN order_lines ol ON s.order_id = ol.order_id
        WHERE s.order_status IN ('Shipped', 'Completed')
        ORDER BY s.order_id, ol.order_line_id
    """)

    order_records = cursor.fetchall()

    # Expand order quantities into individual units
    units = []

    for order_id, order_date, order_line_id, quantity in order_records:
        for _ in range(quantity):
            units.append((order_id, order_date, order_line_id))

    print(f"Eligible order units: {len(units)}")

    target_delivered = 8000

    if len(units) < target_delivered:
        connection.close()
        raise ValueError(
            f"Not enough eligible units for 8000 invoices. "
            f"Available units: {len(units)}"
        )

    rng.shuffle(units)

    # Exactly 8000 delivered shipments.
    # Additional units become non-delivered shipments.
    extra_units = min(1000, len(units) - target_delivered)

    selected_units = units[:target_delivered + extra_units]

    shipments = []
    shipment_lines = []

    for index, (order_id, order_date, order_line_id) in enumerate(
        selected_units, start=1
    ):

        shipment_id = f"SHP-2026-{index:06d}"
        shipment_date = (
            date.fromisoformat(order_date)
            + timedelta(days=rng.randint(2, 12))
        )

        if index <= target_delivered:
            shipment_status = "Delivered"
            delivery_date = (
                shipment_date + timedelta(days=3)
            ).isoformat()
        else:
            shipment_status = rng.choice(["Shipped", "In Transit"])
            delivery_date = None

        shipments.append((
            shipment_id,
            order_id,
            shipment_date.isoformat(),
            delivery_date,
            shipment_status,
            f"TRK-2026-{index:06d}"
        ))

        shipment_lines.append((
            f"SLN-2026-{index:06d}",
            shipment_id,
            order_line_id,
            1
        ))

    cursor.executemany("""
        INSERT INTO shipments (
            shipment_id, order_id, shipment_date,
            delivery_date, shipment_status, tracking_number
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, shipments)

    cursor.executemany("""
        INSERT INTO shipment_lines (
            shipment_line_id, shipment_id,
            order_line_id, shipped_quantity
        )
        VALUES (?, ?, ?, ?)
    """, shipment_lines)

    connection.commit()

    print(f"Total shipments generated: {len(shipments)}")
    print(f"Delivered shipments: {target_delivered}")
    print(f"Non-delivered shipments: {extra_units}")

    connection.close()


def generate_invoices():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            sh.order_id,
            s.account_id,
            sh.shipment_id,
            sh.delivery_date
        FROM shipments sh
        JOIN sales_orders s ON s.order_id = sh.order_id
        WHERE sh.shipment_status = 'Delivered'
        ORDER BY sh.shipment_id
    """)

    delivered_shipments = cursor.fetchall()

    invoices = []
    invoice_lines = []
    invoice_number = 1
    line_number = 1

    for order_id, account_id, shipment_id, delivery_date in delivered_shipments:

        cursor.execute("""
            SELECT
                sl.order_line_id,
                sl.shipped_quantity,
                ol.unit_price
            FROM shipment_lines sl
            JOIN order_lines ol
                ON ol.order_line_id = sl.order_line_id
            WHERE sl.shipment_id = ?
        """, (shipment_id,))

        shipment_items = cursor.fetchall()

        if not shipment_items:
            continue

        invoice_id = f"INV-2026-{invoice_number:06d}"

        invoice_date = date.fromisoformat(delivery_date)
        due_date = invoice_date + timedelta(days=30)

        invoice_total = 0
        current_lines = []

        for order_line_id, quantity, unit_price in shipment_items:

            line_amount = round(quantity * unit_price, 2)
            invoice_total += line_amount

            current_lines.append((
                f"ILN-2026-{line_number:06d}",
                invoice_id,
                order_line_id,
                quantity,
                unit_price,
                line_amount
            ))

            line_number += 1

        invoices.append((
            invoice_id,
            order_id,
            account_id,
            invoice_date.isoformat(),
            due_date.isoformat(),
            "Issued",
            round(invoice_total, 2),
            "INR"
        ))

        invoice_lines.extend(current_lines)
        invoice_number += 1

    cursor.executemany("""
        INSERT INTO invoices (
            invoice_id, order_id, account_id,
            invoice_date, due_date, invoice_status,
            total_amount, currency
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, invoices)

    cursor.executemany("""
        INSERT INTO invoice_lines (
            invoice_line_id, invoice_id, order_line_id,
            quantity, unit_price, line_amount
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, invoice_lines)

    connection.commit()

    print(f"Delivered shipments found: {len(delivered_shipments)}")
    print(f"Total invoices generated: {len(invoices)}")
    print(f"Total invoice lines generated: {len(invoice_lines)}")

    connection.close()



def generate_payments():
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

    print(f"Invoices found for payment generation: {len(invoice_records)}")

    payments = []
    payment_number = 1

    payment_methods = [
        "Bank Transfer",
        "UPI",
        "Credit Card",
        "Cheque"
    ]

    for invoice_index, (invoice_id, account_id, invoice_date, total_amount) in enumerate(invoice_records, start=1):

        payment_count = 2 if invoice_index <= 7000 else 1

        remaining_amount = total_amount

        for payment_index in range(payment_count):

            payment_id = f"PAY-2026-{payment_number:06d}"

            payment_date = (
                date.fromisoformat(invoice_date)
                + timedelta(days=rng.randint(1, 45))
            )

            payment_status = rng.choices(
                ["Received", "Pending", "Failed"],
                weights=[75, 15, 10]
            )[0]

            if payment_index == payment_count - 1:
                payment_amount = remaining_amount
            else:
                payment_amount = round(
                    remaining_amount * rng.uniform(0.2, 0.6), 2
                )

            payment_amount = max(0.01, round(payment_amount, 2))

            if payment_status != "Received":
                payment_amount = round(
                    total_amount * rng.uniform(0.1, 0.5), 2
                )

            payments.append((
                payment_id,
                account_id,
                payment_date.isoformat(),
                payment_amount,
                rng.choice(payment_methods),
                f"REF-2026-{payment_number:06d}",
                payment_status,
                "INR"
            ))

            if payment_status == "Received":
                remaining_amount = max(
                    0,
                    round(remaining_amount - payment_amount, 2)
                )

            payment_number += 1

    cursor.executemany("""
        INSERT INTO payments (
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

    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT payment_id, account_id, payment_date, payment_amount
        FROM payments
        WHERE payment_status = 'Received'
        ORDER BY payment_id
    """)

    payment_records = cursor.fetchall()

    cursor.execute("""
        SELECT
    i.invoice_id,
    i.account_id,
    i.invoice_date,
    i.total_amount,
    COALESCE(SUM(pa.allocated_amount), 0)
        FROM invoices i
        LEFT JOIN payment_allocations pa
            ON i.invoice_id = pa.invoice_id
        GROUP BY i.invoice_id
        ORDER BY i.invoice_id
    """)

    invoice_records = cursor.fetchall()

    invoice_balances = {}

    for invoice_id, account_id, invoice_date, total_amount, allocated_amount in invoice_records:
        invoice_balances[invoice_id] = {
            "account_id": account_id,
            "invoice_date": invoice_date,
            "outstanding": max(
                0,
                round(total_amount - allocated_amount, 2)
            )
        }

    print(f"Received payments found: {len(payment_records)}")

    allocations = []
    allocation_number = 1

    for payment_id, account_id, payment_date, payment_amount in payment_records:

        remaining_payment = round(payment_amount, 2)

        for invoice_id, invoice_data in invoice_balances.items():

            if remaining_payment <= 0:
                break

            if invoice_data["account_id"] != account_id:
                continue

            if invoice_data["invoice_date"] > payment_date:
                continue

            outstanding = invoice_data["outstanding"]

            if outstanding <= 0:
                continue

            allocated_amount = round(
                min(remaining_payment, outstanding), 2
            )

            if allocated_amount <= 0:
                continue

            allocations.append((
                f"ALLOC-2026-{allocation_number:06d}",
                payment_id,
                invoice_id,
                allocated_amount,
                payment_date
            ))

            invoice_data["outstanding"] = round(
                outstanding - allocated_amount, 2
            )

            remaining_payment = round(
                remaining_payment - allocated_amount, 2
            )

            allocation_number += 1

    cursor.executemany("""
        INSERT INTO payment_allocations (
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
    dispute_number = 1

    dispute_reasons = [
        "Incorrect invoice amount",
        "Damaged goods",
        "Missing items",
        "Incorrect product quantity",
        "Duplicate invoice"
    ]

    for invoice_id, account_id, invoice_date, total_amount in invoice_records:

        if rng.random() > 0.10:
            continue

        dispute_id = f"DSP-2026-{dispute_number:06d}"

        dispute_date = (
            date.fromisoformat(invoice_date)
            + timedelta(days=rng.randint(1, 15))
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

        dispute_number += 1

    cursor.executemany("""
        INSERT INTO disputes (
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
    connection.execute("PRAGMA foreign_keys = ON")
    cursor = connection.cursor()

    events = []
    event_number = 1

    print("\nGenerating status events...")

    def add_event(entity_type, entity_id, previous_status,
                  new_status, event_date, description):

        nonlocal event_number

        events.append((
            f"EVT-2026-{event_number:06d}",
            entity_type,
            entity_id,
            previous_status,
            new_status,
            event_date,
            description
        ))

        event_number += 1

    # 1. Quote events

    cursor.execute("""
        SELECT quote_id, quote_date, quote_status
        FROM quotes
        ORDER BY quote_id
    """)

    for quote_id, quote_date, final_status in cursor.fetchall():

        event_date = date.fromisoformat(quote_date)

        add_event(
            "Quote", quote_id, "Draft", "Sent",
            event_date.isoformat(), "Quote sent to customer"
        )

        if final_status != "Sent":

            add_event(
                "Quote", quote_id, "Sent", final_status,
                (event_date + timedelta(days=1)).isoformat(),
                f"Quote status changed to {final_status}"
            )

    # 2. Sales order events

    cursor.execute("""
        SELECT order_id, order_date, order_status
        FROM sales_orders
        ORDER BY order_id
    """)

    order_status_flow = [
        "Confirmed",
        "Processing",
        "Shipped",
        "Completed"
    ]

    for order_id, order_date, final_status in cursor.fetchall():

        event_date = date.fromisoformat(order_date)
        previous_status = "Created"

        final_index = order_status_flow.index(final_status)

        for index in range(final_index + 1):

            new_status = order_status_flow[index]

            add_event(
                "SalesOrder",
                order_id,
                previous_status,
                new_status,
                (event_date + timedelta(days=index)).isoformat(),
                f"Order status changed to {new_status}"
            )

            previous_status = new_status

    # 3. Shipment events

    cursor.execute("""
        SELECT shipment_id, shipment_date,
               delivery_date, shipment_status
        FROM shipments
        ORDER BY shipment_id
    """)

    for shipment_id, shipment_date, delivery_date, final_status in cursor.fetchall():

        shipment_date = date.fromisoformat(shipment_date)

        add_event(
            "Shipment", shipment_id, "Created", "Shipped",
            shipment_date.isoformat(), "Shipment dispatched"
        )

        if final_status in ("In Transit", "Delivered"):

            transit_date = shipment_date + timedelta(days=1)

            add_event(
                "Shipment", shipment_id, "Shipped", "In Transit",
                transit_date.isoformat(), "Shipment in transit"
            )

        if final_status == "Delivered":

            add_event(
                "Shipment", shipment_id, "In Transit", "Delivered",
                delivery_date, "Shipment delivered"
            )

    # 4. Invoice events

    cursor.execute("""
        SELECT invoice_id, invoice_date, invoice_status
        FROM invoices
        ORDER BY invoice_id
    """)

    for invoice_id, invoice_date, invoice_status in cursor.fetchall():

        add_event(
            "Invoice", invoice_id, "Draft", invoice_status,
            invoice_date, f"Invoice status changed to {invoice_status}"
        )

    # 5. Payment events

    cursor.execute("""
        SELECT payment_id, payment_date, payment_status
        FROM payments
        ORDER BY payment_id
    """)

    for payment_id, payment_date, payment_status in cursor.fetchall():

        add_event(
            "Payment", payment_id, "Initiated", payment_status,
            payment_date, f"Payment status changed to {payment_status}"
        )

    # 6. Dispute events

    cursor.execute("""
        SELECT dispute_id, dispute_date,
               resolution_date, dispute_status
        FROM disputes
        ORDER BY dispute_id
    """)

    for dispute_id, dispute_date, resolution_date, dispute_status in cursor.fetchall():

        add_event(
            "Dispute", dispute_id, "None", "Open",
            dispute_date, "Dispute raised"
        )

        if dispute_status != "Open":

            status_date = resolution_date if dispute_status == "Resolved" else dispute_date

            add_event(
                "Dispute", dispute_id, "Open", dispute_status,
                status_date, f"Dispute status changed to {dispute_status}"
            )

    cursor.executemany("""
        INSERT INTO status_events (
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

    cursor.execute("""
        SELECT entity_type, COUNT(*)
        FROM status_events
        GROUP BY entity_type
        ORDER BY entity_type
    """)

    print("\nEvents by entity:")

    for entity_type, count in cursor.fetchall():
        print(f"{entity_type}: {count}")

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

