# O2C Revenue Intelligence Dashboard

An Order-to-Cash (O2C) Revenue Intelligence application built using Python, SQLite, Pandas, Streamlit and Plotly.

## Project Overview

This project models the Order-to-Cash workflow:

Quotes → Sales Orders → Shipments → Invoices → Payments → Disputes

It monitors business transactions, outstanding receivables, payment allocations and operational exceptions.

## Technology Stack

- Python
- SQLite
- Pandas
- Streamlit
- Plotly
- Pytest

## Database Design

The database contains 13 relational tables:

1. Accounts
2. Quotes
3. Quote Lines
4. Sales Orders
5. Order Lines
6. Shipments
7. Shipment Lines
8. Invoices
9. Invoice Lines
10. Payments
11. Payment Allocations
12. Disputes
13. Status Events

## Dashboard Features

- Overview
- Order Management
- Shipment Tracking
- Invoice Management
- Payment Management
- Dispute Management
- Exception Monitoring
- Data Validation

## Anomaly Detection

Five deterministic anomalies are included:

1. Overbilling: Invoice quantity exceeds delivered quantity.
2. Duplicate Payment Allocation: A payment is allocated twice to the same invoice.
3. Completed Order with Unpaid Invoice: A completed order has an outstanding invoice.
4. Invalid Lifecycle Transition: An order has an invalid status transition.
5. Missing Dispute Reconciliation: An active dispute is missing from the receivables report.

Expected anomaly records are available in exports/ground_truth.csv.

## Dataset

| Entity | Records |
|---|---:|
| Accounts | 500 |
| Quotes | 10,000 |
| Sales Orders | 7,000 |
| Shipments | 3,454 |
| Invoices | 1,145 |
| Payments | 1,145 |
| Payment Allocations | 388 |
| Disputes | 125 |
| Status Events | 36,451 |

The dataset is synthetic and uses a fixed random seed.

## Installation and Setup

Clone the repository:

```bash
git clone https://github.com/durga-naga/o2c-revenue-intelligence.git
cd o2c-revenue-intelligence
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Dashboard

```bash
streamlit run app.py
```

## Verify Anomalies

```bash
python data_generator/verify_anomalies.py
```

## Run Tests

```bash
pytest -v
```

The current test suite contains 8 tests covering database integrity, foreign keys, table structure and anomaly scenarios.

## Data Exports

The exports folder contains:

- o2c_database.sql
- o2c_database.json
- receivables_report.csv
- ground_truth.csv

## Assumptions and Limitations

- The application uses synthetic transaction data.
- The current dataset contains 1,145 invoices and 1,145 payments.
- The receivables report is generated separately.
- The five injected anomalies are deterministic.
- This is a demonstration project, not a production financial system.

## AI Assistance Disclosure

AI assistance was used for code guidance, debugging, documentation support and test-case development. Generated code and outputs were reviewed and tested during implementation.

## Future Improvements

- Expand transaction volumes.
- Improve receivables calculations.
- Add more financial validation rules.
- Enhance dashboard filtering.
- Add automated data quality monitoring.