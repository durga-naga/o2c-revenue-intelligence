
import sqlite3
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "o2c_database.db"
OUTPUT_PATH = BASE_DIR / "exports" / "receivables_report.csv"

# Deliberately omit this dispute from the receivables report.
ANOMALY_DISPUTE_ID = "DSP-2026-000004"


def generate_receivables_report():

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
    SELECT
        i.invoice_id,
        i.total_amount,
        COALESCE((
            SELECT SUM(pa.allocated_amount)
            FROM payment_allocations pa
            WHERE pa.invoice_id = i.invoice_id
        ), 0) AS allocated_amount
    FROM invoices i
    ORDER BY i.invoice_id
""")

    invoices = cursor.fetchall()

    cursor.execute("""
        SELECT dispute_id, invoice_id, disputed_amount
        FROM disputes
        WHERE dispute_status IN ('Open', 'Under Review')
    """)

    disputes = cursor.fetchall()
    connection.close()

    dispute_map = {}

    for dispute_id, invoice_id, amount in disputes:
        if invoice_id not in dispute_map:
            dispute_map[invoice_id] = 0

        if dispute_id != ANOMALY_DISPUTE_ID:
            dispute_map[invoice_id] += amount

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)

        writer.writerow([
            "invoice_id",
            "invoice_amount",
            "allocated_amount",
            "disputed_amount_in_receivables",
            "outstanding_balance"
        ])

        for invoice_id, invoice_amount, allocated_amount in invoices:

            disputed_amount = dispute_map.get(invoice_id, 0)

            outstanding = round(
                invoice_amount - allocated_amount,
                2
            )

            writer.writerow([
                invoice_id,
                invoice_amount,
                allocated_amount,
                disputed_amount,
                outstanding
            ])

    print("Receivables report generated successfully!")
    print("Deliberately omitted dispute:", ANOMALY_DISPUTE_ID)
    print("Output:", OUTPUT_PATH)


if __name__ == "__main__":
    generate_receivables_report()
