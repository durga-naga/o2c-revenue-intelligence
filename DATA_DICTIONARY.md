# Detailed Data Dictionary

## 1. Overview

This document describes the database structure, fields, data types, required and optional attributes, allowed values, units, uniqueness rules, relationships, and validation guidelines used in the O2C Revenue Intelligence Dashboard.

The database contains 13 relational tables and uses synthetic data generated with a fixed random seed (20261022).

**General conventions:**
- Primary keys uniquely identify records.
- Foreign keys maintain relationships between related tables.
- Required fields are defined using `NOT NULL`.
- Optional fields allow NULL values.
- Monetary values are represented in INR.
- Quantity fields represent units of products.
- Date and timestamp fields are stored as TEXT.
- Allowed status values are defined by the data generator; the database schema does not enforce them through CHECK constraints.

## 2. Table Definitions

### 2.1 Accounts

Stores customer and business account information.

| Field | Type | Required | Rules |
|---|---|---|---|
| account_id | TEXT | Yes | Primary key; unique account ID |
| account_name | TEXT | Yes | Account name; not empty |
| industry | TEXT | No | Education, Healthcare, Retail, Manufacturing, Technology |
| country | TEXT | No | India, USA, UK, Germany, Australia |
| created_at | TEXT | Yes | Valid account creation timestamp |

### 2.2 Quotes

Stores customer quotations.

| Field | Type | Required | Rules |
|---|---|---|---|
| quote_id | TEXT | Yes | Primary key; unique quote ID |
| account_id | TEXT | Yes | Foreign key referencing accounts |
| quote_date | TEXT | Yes | Valid quote date |
| expiry_date | TEXT | No | Valid expiry date |
| quote_status | TEXT | Yes | Draft, Sent, Accepted, Rejected, Expired |
| total_amount | REAL | Yes | Monetary amount in INR |
| currency | TEXT | Yes | INR |

### 2.3 Quote Lines

Stores individual products and quantities included in a quote.

| Field | Type | Required | Rules |
|---|---|---|---|
| quote_line_id | TEXT | Yes | Primary key |
| quote_id | TEXT | Yes | Foreign key referencing quotes |
| product_name | TEXT | Yes | Laptop, Desktop, Monitor, Keyboard, Mouse, Printer |
| quantity | INTEGER | Yes | Product quantity; positive integer |
| unit_price | REAL | Yes | Price per unit in INR |
| line_amount | REAL | Yes | Quantity × unit price |

### 2.4 Sales Orders

Stores orders created from customer quotes.

| Field | Type | Required | Rules |
|---|---|---|---|
| order_id | TEXT | Yes | Primary key; unique order ID |
| quote_id | TEXT | Yes | Foreign key referencing quotes |
| account_id | TEXT | Yes | Foreign key referencing accounts |
| order_date | TEXT | Yes | Valid order date |
| order_status | TEXT | Yes | Created, Confirmed, Processing, Shipped, Completed, Cancelled |
| total_amount | REAL | Yes | Total order value in INR |

### 2.5 Order Lines

Stores individual products in sales orders.

| Field | Type | Required | Rules |
|---|---|---|---|
| order_line_id | TEXT | Yes | Primary key |
| order_id | TEXT | Yes | Foreign key referencing sales_orders |
| product_name | TEXT | Yes | Product name from the defined product list |
| quantity | INTEGER | Yes | Ordered quantity; positive integer |
| unit_price | REAL | Yes | Price per unit in INR |
| line_amount | REAL | Yes | Quantity × unit price |

### 2.6 Shipments

Stores shipment and delivery information.

| Field | Type | Required | Rules |
|---|---|---|---|
| shipment_id | TEXT | Yes | Primary key |
| order_id | TEXT | Yes | Foreign key referencing sales_orders |
| shipment_date | TEXT | Yes | Valid shipment date |
| delivery_date | TEXT | No | Valid delivery date, when available |
| shipment_status | TEXT | Yes | Preparing, Shipped, In Transit, Delivered |
| tracking_number | TEXT | No | Shipment tracking reference |

### 2.7 Shipment Lines

Connects shipments with individual order lines.

| Field | Type | Required | Rules |
|---|---|---|---|
| shipment_line_id | TEXT | Yes | Primary key |
| shipment_id | TEXT | Yes | Foreign key referencing shipments |
| order_line_id | TEXT | Yes | Foreign key referencing order_lines |
| shipped_quantity | INTEGER | Yes | Quantity shipped; positive integer |

### 2.8 Invoices

Stores invoice details associated with sales orders.

| Field | Type | Required | Rules |
|---|---|---|---|
| invoice_id | TEXT | Yes | Primary key; unique invoice ID |
| order_id | TEXT | Yes | Foreign key referencing sales_orders |
| account_id | TEXT | Yes | Foreign key referencing accounts |
| invoice_date | TEXT | Yes | Valid invoice date |
| due_date | TEXT | Yes | Invoice payment due date |
| invoice_status | TEXT | Yes | Draft, Issued, Partially Paid, Paid, Overdue |
| total_amount | REAL | Yes | Invoice amount in INR |
| currency | TEXT | Yes | INR |

### 2.9 Invoice Lines

Stores product-level invoice details.

| Field | Type | Required | Rules |
|---|---|---|---|
| invoice_line_id | TEXT | Yes | Primary key |
| invoice_id | TEXT | Yes | Foreign key referencing invoices |
| order_line_id | TEXT | Yes | Foreign key referencing order_lines |
| quantity | INTEGER | Yes | Invoiced quantity; positive integer |
| unit_price | REAL | Yes | Price per unit in INR |
| line_amount | REAL | Yes | Quantity × unit price |

### 2.10 Payments

Stores payments received from customer accounts.

| Field | Type | Required | Rules |
|---|---|---|---|
| payment_id | TEXT | Yes | Primary key; unique payment ID |
| account_id | TEXT | Yes | Foreign key referencing accounts |
| payment_date | TEXT | Yes | Valid payment date |
| payment_amount | REAL | Yes | Payment amount in INR |
| payment_method | TEXT | No | Payment method, when available |
| payment_reference | TEXT | No | External payment reference |
| payment_status | TEXT | Yes | Received, Pending, Failed |
| currency | TEXT | Yes | INR |

### 2.11 Payment Allocations

Connects payments with invoices and records allocated amounts.

| Field | Type | Required | Rules |
|---|---|---|---|
| allocation_id | TEXT | Yes | Primary key |
| payment_id | TEXT | Yes | Foreign key referencing payments |
| invoice_id | TEXT | Yes | Foreign key referencing invoices |
| allocated_amount | REAL | Yes | Allocated payment amount in INR |
| allocation_date | TEXT | Yes | Valid allocation date |

This table supports the many-to-many relationship between payments and invoices.

### 2.12 Disputes

Stores customer invoice disputes and their resolution details.

| Field | Type | Required | Rules |
|---|---|---|---|
| dispute_id | TEXT | Yes | Primary key; unique dispute ID |
| invoice_id | TEXT | Yes | Foreign key referencing invoices |
| account_id | TEXT | Yes | Foreign key referencing accounts |
| dispute_date | TEXT | Yes | Valid dispute date |
| dispute_reason | TEXT | Yes | Description of dispute reason |
| disputed_amount | REAL | Yes | Disputed amount in INR |
| dispute_status | TEXT | Yes | Open, Under Review, Resolved |
| resolution_date | TEXT | No | Resolution date, when available |

### 2.13 Status Events

Maintains historical status changes for business entities.

| Field | Type | Required | Rules |
|---|---|---|---|
| event_id | TEXT | Yes | Primary key |
| entity_type | TEXT | Yes | Type of business entity |
| entity_id | TEXT | Yes | Identifier of the related entity |
| previous_status | TEXT | No | Previous lifecycle status |
| new_status | TEXT | Yes | New lifecycle status |
| event_timestamp | TEXT | Yes | Valid event timestamp |
| event_description | TEXT | No | Description of the status change |

Status events preserve lifecycle history. The entity_id field is polymorphic and does not have a direct foreign key constraint.

## 3. Primary Key and Foreign Key Relationships

| Parent Table | Child Table | Relationship |
|---|---|---|
| Accounts | Quotes | One-to-Many |
| Quotes | Quote Lines | One-to-Many |
| Quotes | Sales Orders | One-to-Many |
| Accounts | Sales Orders | One-to-Many |
| Sales Orders | Order Lines | One-to-Many |
| Sales Orders | Shipments | One-to-Many |
| Shipments | Shipment Lines | One-to-Many |
| Order Lines | Shipment Lines | One-to-Many |
| Sales Orders | Invoices | One-to-Many |
| Accounts | Invoices | One-to-Many |
| Invoices | Invoice Lines | One-to-Many |
| Order Lines | Invoice Lines | One-to-Many |
| Accounts | Payments | One-to-Many |
| Payments | Payment Allocations | One-to-Many |
| Invoices | Payment Allocations | One-to-Many |
| Invoices | Disputes | One-to-Many |
| Accounts | Disputes | One-to-Many |

Payment Allocations provide the bridge between Payments and Invoices. Status Events maintain historical references to business entities.

## 4. Validation Guidelines

The following validation rules are used to maintain data quality:

1. Primary key values must be unique and non-null.
2. Foreign key references must point to existing parent records.
3. Required fields must not contain NULL values.
4. Status fields must use the allowed values defined by the data generator.
5. Dates and timestamps must contain valid date/time values.
6. Quantities must be positive integers for normal business records.
7. Line amounts must reconcile with quantity multiplied by unit price.
8. Invoice quantities must be checked against fulfilled shipment quantities.
9. Payment allocations must be checked for duplicate allocation scenarios.
10. Payment and invoice balances must be reconciled.
11. Lifecycle transitions must follow valid business sequences.
12. Disputes must be considered during receivables reconciliation.

Deliberate anomaly scenarios are separately identified and documented in the ground-truth export.

## 5. Data Generation and Provenance

All business records are synthetically generated using Python. No external customer datasets or confidential personal information are used.

The generator uses a fixed random seed of `20261022` to support repeatable dataset generation.

The database schema is maintained in `database/schema.sql`.
