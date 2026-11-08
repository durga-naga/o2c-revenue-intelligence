
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "o2c_test_v2.db"

st.set_page_config(
    page_title="O2C Revenue Intelligence",
    page_icon="📊",
    layout="wide"
)


@st.cache_data
def load_data(query):
    connection = sqlite3.connect(DB_PATH)
    data = pd.read_sql_query(query, connection)
    connection.close()
    return data


def show_table(query):
    data = load_data(query)
    st.dataframe(data, use_container_width=True)
    return data


st.title("O2C Revenue Intelligence Dashboard")
st.caption("Order-to-Cash | Revenue Monitoring | Exception Detection")

if not DB_PATH.exists():
    st.error("Database not found. Please generate the database first.")
    st.stop()


# Sidebar navigation
page = st.sidebar.selectbox(
    "Navigation",
    [
        "Overview",
        "Order Management",
        "Shipment Tracking",
        "Invoice Management",
        "Payment Management",
        "Dispute Management",
        "Exception Monitoring",
        "Data Validation"
    ]
)


# 1. OVERVIEW
if page == "Overview":

    st.header("Business Overview")

    accounts = load_data("SELECT COUNT(*) AS total FROM accounts").iloc[0, 0]
    quotes = load_data("SELECT COUNT(*) AS total FROM quotes").iloc[0, 0]
    orders = load_data("SELECT COUNT(*) AS total FROM sales_orders").iloc[0, 0]
    invoices = load_data("SELECT COUNT(*) AS total FROM invoices").iloc[0, 0]

    collected = load_data("""
        SELECT COALESCE(SUM(allocated_amount), 0) AS total
        FROM payment_allocations
    """).iloc[0, 0]

    receivables = load_data("""
        SELECT COALESCE(SUM(i.total_amount), 0) -
               COALESCE((
                   SELECT SUM(pa.allocated_amount)
                   FROM payment_allocations pa
               ), 0) AS total
        FROM invoices i
    """).iloc[0, 0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Accounts", f"{accounts:,}")
    c2.metric("Total Quotes", f"{quotes:,}")
    c3.metric("Sales Orders", f"{orders:,}")
    c4.metric("Invoices", f"{invoices:,}")

    c5, c6 = st.columns(2)
    c5.metric("Collected Revenue", f"₹{collected:,.2f}")
    c6.metric("Outstanding Receivables", f"₹{receivables:,.2f}")

    st.subheader("Order Status Distribution")

    order_status = load_data("""
        SELECT order_status, COUNT(*) AS count
        FROM sales_orders
        GROUP BY order_status
    """)

    fig = px.bar(
        order_status,
        x="order_status",
        y="count",
        title="Sales Orders by Status"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Invoice Status Distribution")

    invoice_status = load_data("""
        SELECT invoice_status, COUNT(*) AS count
        FROM invoices
        GROUP BY invoice_status
    """)

    st.dataframe(invoice_status, use_container_width=True)


# 2. ORDER MANAGEMENT
elif page == "Order Management":

    st.header("Order Management")

    show_table("""
        SELECT
            s.order_id,
            s.quote_id,
            a.account_name,
            s.order_date,
            s.order_status,
            s.total_amount
        FROM sales_orders s
        JOIN accounts a ON s.account_id = a.account_id
        ORDER BY s.order_date DESC
    """)


# 3. SHIPMENT TRACKING
elif page == "Shipment Tracking":

    st.header("Shipment Tracking")

    show_table("""
        SELECT
            sh.shipment_id,
            sh.order_id,
            sh.shipment_date,
            sh.delivery_date,
            sh.shipment_status,
            sh.tracking_number
        FROM shipments sh
        ORDER BY sh.shipment_date DESC
    """)


# 4. INVOICE MANAGEMENT
elif page == "Invoice Management":

    st.header("Invoice Management")

    show_table("""
        SELECT
            invoice_id,
            order_id,
            account_id,
            invoice_date,
            due_date,
            invoice_status,
            total_amount,
            currency
        FROM invoices
        ORDER BY invoice_date DESC
    """)


# 5. PAYMENT MANAGEMENT
elif page == "Payment Management":

    st.header("Payment Management")

    show_table("""
        SELECT
            p.payment_id,
            p.account_id,
            p.payment_date,
            p.payment_amount,
            p.payment_method,
            p.payment_status,
            COALESCE(SUM(pa.allocated_amount), 0) AS allocated_amount
        FROM payments p
        LEFT JOIN payment_allocations pa
            ON p.payment_id = pa.payment_id
        GROUP BY p.payment_id
        ORDER BY p.payment_date DESC
    """)


# 6. DISPUTE MANAGEMENT
elif page == "Dispute Management":

    st.header("Dispute Management")

    show_table("""
        SELECT
            dispute_id,
            invoice_id,
            account_id,
            dispute_date,
            dispute_reason,
            disputed_amount,
            dispute_status
        FROM disputes
        ORDER BY dispute_date DESC
    """)


# 7. EXCEPTION MONITORING
elif page == "Exception Monitoring":

    st.header("Exception Monitoring")

    st.subheader("Overbilling Exceptions")

    show_table("""
        SELECT
            il.invoice_id,
            il.order_line_id,
            il.quantity AS invoiced_quantity,
            COALESCE(SUM(sl.shipped_quantity), 0) AS delivered_quantity
        FROM invoice_lines il
        JOIN shipments sh
            ON sh.order_id = (
                SELECT order_id
                FROM order_lines
                WHERE order_line_id = il.order_line_id
            )
            AND sh.shipment_status = 'Delivered'
        JOIN shipment_lines sl
            ON sl.shipment_id = sh.shipment_id
            AND sl.order_line_id = il.order_line_id
        GROUP BY il.invoice_line_id
        HAVING invoiced_quantity > delivered_quantity
    """)

    st.subheader("Duplicate Payment Allocations")

    show_table("""
        SELECT
            payment_id,
            invoice_id,
            COUNT(*) AS allocation_count,
            SUM(allocated_amount) AS total_allocated
        FROM payment_allocations
        GROUP BY payment_id, invoice_id
        HAVING COUNT(*) > 1
    """)

    st.subheader("Invalid Lifecycle Events")

    show_table("""
        SELECT *
        FROM status_events
        WHERE previous_status = 'Created'
          AND new_status = 'Completed'
    """)

    st.subheader("Completed Orders with Outstanding Invoices")

    show_table("""
        SELECT
            i.invoice_id,
            i.order_id,
            i.total_amount,
            COALESCE(SUM(pa.allocated_amount), 0) AS allocated_amount,
            i.total_amount - COALESCE(SUM(pa.allocated_amount), 0)
                AS outstanding_balance
        FROM invoices i
        JOIN sales_orders s ON i.order_id = s.order_id
        LEFT JOIN payment_allocations pa ON i.invoice_id = pa.invoice_id
        WHERE s.order_status = 'Completed'
        GROUP BY i.invoice_id
        HAVING outstanding_balance > 0
    """)


# 8. DATA VALIDATION
elif page == "Data Validation":

    st.header("Database Validation")

    connection = sqlite3.connect(DB_PATH)
    foreign_key_errors = connection.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    integrity_result = connection.execute(
        "PRAGMA integrity_check"
    ).fetchone()[0]

    connection.close()

    c1, c2 = st.columns(2)

    c1.metric(
        "Foreign Key Errors",
        len(foreign_key_errors)
    )

    c2.metric(
        "Database Integrity",
        integrity_result
    )

    if not foreign_key_errors and integrity_result == "ok":
        st.success("Database validation passed!")
    else:
        st.error("Database validation found issues.")

    st.subheader("Table Record Counts")

    table_names = [
        "accounts", "quotes", "quote_lines",
        "sales_orders", "order_lines",
        "shipments", "shipment_lines",
        "invoices", "invoice_lines",
        "payments", "payment_allocations",
        "disputes", "status_events"
    ]

    counts = []

    connection = sqlite3.connect(DB_PATH)

    for table in table_names:
        count = connection.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        counts.append({
            "table_name": table,
            "record_count": count
        })

    connection.close()

    st.dataframe(
        pd.DataFrame(counts),
        use_container_width=True
    )
