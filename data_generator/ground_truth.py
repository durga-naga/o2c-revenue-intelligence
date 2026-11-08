import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = BASE_DIR / "exports" / "ground_truth.csv"


def generate_ground_truth():

    anomalies = [
        {
            "entity_type": "Invoice",
            "entity_id": "INV-2026-000001",
            "anomaly_type": "OVERBILLING",
            "description": "Invoice quantity exceeds delivered quantity"
        },
        {
            "entity_type": "Payment",
            "entity_id": "PAY-2026-000002",
            "anomaly_type": "DUPLICATE_ALLOCATION",
            "description": "Same payment is allocated to the same invoice more than once"
        },
        {
            "entity_type": "Invoice",
            "entity_id": "INV-2026-000003",
            "anomaly_type": "UNPAID_CLOSED_ORDER",
            "description": "Completed order has an invoice with outstanding balance"
        },
        {
            "entity_type": "SalesOrder",
            "entity_id": "SO-2026-000001",
            "anomaly_type": "INVALID_LIFECYCLE",
            "description": "Order status transition skips required intermediate states"
        },
        {
            "entity_type": "Dispute",
            "entity_id": "DSP-2026-000004",
            "anomaly_type": "MISSING_DISPUTE_RECONCILIATION",
            "description": "Active dispute is missing from the receivables report"
        }
    ]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "entity_type",
                "entity_id",
                "anomaly_type",
                "description"
            ]
        )

        writer.writeheader()
        writer.writerows(anomalies)

    print("Ground truth generated successfully!")
    print("Total anomaly labels:", len(anomalies))
    print("Output:", OUTPUT_PATH)


if __name__ == "__main__":
    generate_ground_truth()