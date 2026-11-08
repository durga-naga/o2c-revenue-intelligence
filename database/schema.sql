CREATE TABLE IF NOT EXISTS accounts (
    account_id TEXT PRIMARY KEY,
    account_name TEXT NOT NULL,
    industry TEXT,
    country TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS quotes (
    quote_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    quote_date TEXT NOT NULL,
    expiry_date TEXT,
    quote_status TEXT NOT NULL,
    total_amount REAL NOT NULL,
    currency TEXT NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);
CREATE TABLE IF NOT EXISTS quote_lines (
    quote_line_id TEXT PRIMARY KEY,
    quote_id TEXT NOT NULL,
    product_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    line_amount REAL NOT NULL,
    FOREIGN KEY (quote_id) REFERENCES quotes(quote_id)
);
CREATE TABLE IF NOT EXISTS sales_orders (
    order_id TEXT PRIMARY KEY,
    quote_id TEXT NOT NULL,
    account_id TEXT NOT NULL,
    order_date TEXT NOT NULL,
    order_status TEXT NOT NULL,
    total_amount REAL NOT NULL,
    FOREIGN KEY (quote_id) REFERENCES quotes(quote_id),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);
CREATE TABLE IF NOT EXISTS order_lines (
    order_line_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    product_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    line_amount REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES sales_orders(order_id)
);
CREATE TABLE IF NOT EXISTS shipments (
    shipment_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    shipment_date TEXT NOT NULL,
    delivery_date TEXT,
    shipment_status TEXT NOT NULL,
    tracking_number TEXT,
    FOREIGN KEY (order_id) REFERENCES sales_orders(order_id)
);
CREATE TABLE IF NOT EXISTS shipment_lines (
    shipment_line_id TEXT PRIMARY KEY,
    shipment_id TEXT NOT NULL,
    order_line_id TEXT NOT NULL,
    shipped_quantity INTEGER NOT NULL,
    FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id),
    FOREIGN KEY (order_line_id) REFERENCES order_lines(order_line_id)
);
CREATE TABLE IF NOT EXISTS invoices (
    invoice_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    account_id TEXT NOT NULL,
    invoice_date TEXT NOT NULL,
    due_date TEXT NOT NULL,
    invoice_status TEXT NOT NULL,
    total_amount REAL NOT NULL,
    currency TEXT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES sales_orders(order_id),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);
CREATE TABLE IF NOT EXISTS invoice_lines (
    invoice_line_id TEXT PRIMARY KEY,
    invoice_id TEXT NOT NULL,
    order_line_id TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    line_amount REAL NOT NULL,
    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id),
    FOREIGN KEY (order_line_id) REFERENCES order_lines(order_line_id)
);
CREATE TABLE IF NOT EXISTS payments (
    payment_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    payment_date TEXT NOT NULL,
    payment_amount REAL NOT NULL,
    payment_method TEXT,
    payment_reference TEXT,
    payment_status TEXT NOT NULL,
    currency TEXT NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);
CREATE TABLE IF NOT EXISTS payment_allocations (
    allocation_id TEXT PRIMARY KEY,
    payment_id TEXT NOT NULL,
    invoice_id TEXT NOT NULL,
    allocated_amount REAL NOT NULL,
    allocation_date TEXT NOT NULL,
    FOREIGN KEY (payment_id) REFERENCES payments(payment_id),
    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id)
);
CREATE TABLE IF NOT EXISTS disputes (
    dispute_id TEXT PRIMARY KEY,
    invoice_id TEXT NOT NULL,
    account_id TEXT NOT NULL,
    dispute_date TEXT NOT NULL,
    dispute_reason TEXT NOT NULL,
    disputed_amount REAL NOT NULL,
    dispute_status TEXT NOT NULL,
    resolution_date TEXT,
    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);
CREATE TABLE IF NOT EXISTS status_events (
    event_id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    previous_status TEXT,
    new_status TEXT NOT NULL,
    event_timestamp TEXT NOT NULL,
    event_description TEXT
);