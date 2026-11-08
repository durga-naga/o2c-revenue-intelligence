# O2C Revenue Intelligence Dashboard

An Order-to-Cash (O2C) Revenue Intelligence application built using Python, SQLite, Pandas, Streamlit, and Plotly.

**Live Dashboard:** [Open O2C Revenue Intelligence Dashboard](https://o2c-revenue-intelligence-bqgrotfziqexuy58gyqpvo.streamlit.app/)

**GitHub Repository:** [View Source Code](https://github.com/durga-naga/o2c-revenue-intelligence)

## Project Overview

This project models the Order-to-Cash workflow:

Quotes → Sales Orders → Shipments → Invoices → Payments → Disputes

It monitors business transactions, outstanding receivables, payment allocations, and operational exceptions.

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

1. **Overbilling:** Invoice quantity exceeds fulfilled shipment quantity.
2. **Duplicate Payment Allocation:** A payment is allocated more than once to the same invoice.
3. **Completed Order with Unpaid Invoice:** A completed order has an outstanding invoice.
4. **Invalid Lifecycle Transition:** An order contains an invalid status transition.
5. **Missing Dispute Reconciliation:** An active dispute is missing from the receivables report.

Expected anomaly records are available in `exports/ground_truth.csv`.

## Dataset

The database contains the following synthetic records:

- Accounts: 500
- Quotes: 10,000
- Quote Lines: 10,000
- Sales Orders: 7,000
- Order Lines: 7,000
- Shipments: 9,000
- Shipment Lines: 9,000
- Invoices: 8,000
- Invoice Lines: 8,000
- Payments: 15,000
- Payment Allocations: 13,901
- Disputes: 806
- Status Events: 86,303

The dataset is generated using a fixed random seed for reproducibility and includes five deterministic anomalies for validation.

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

### Generate the Database and Dataset

Run the following commands in order:

```bash
python database/create_test_database.py
python data_generator/generator.py
python data_generator/anomaly_injector.py
python data_generator/ground_truth.py
python data_generator/receivables_report.py
```

These commands create the database, generate synthetic transaction data, inject anomalies, and generate validation reports.

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

The test suite contains 8 tests covering database integrity, foreign keys, table structure, and anomaly scenarios.

## Data Exports

The `exports` folder contains:

- `receivables_report.csv`
- `ground_truth.csv`
- `o2c_database.sql`
- `o2c_database.json`

## Assumptions and Limitations

- The application uses synthetic transaction data.
- The receivables report is generated separately.
- The five injected anomalies are deterministic.
- This is a demonstration project, not a production financial system.

## AI Assistance Disclosure

AI assistance was used for code guidance, debugging, documentation support, and test-case development. Generated code and outputs were reviewed and tested during implementation.

## Future Improvements

- Add more financial validation rules.
- Improve receivables calculations.
- Enhance dashboard filtering.
- Add automated data quality monitoring.
- Introduce additional anomaly scenarios.