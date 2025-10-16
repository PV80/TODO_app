PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    location TEXT NOT NULL,
    units INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS tenants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    contact TEXT NOT NULL,
    lease_start TEXT NOT NULL,
    lease_end TEXT,
    monthly_rent REAL NOT NULL,
    is_airbnb INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS rent_invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    amount REAL NOT NULL,
    due_date TEXT NOT NULL,
    status TEXT NOT NULL,
    paid_date TEXT
);

CREATE TABLE IF NOT EXISTS maintenance_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    status TEXT NOT NULL,
    vendor TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS scheduled_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient TEXT NOT NULL,
    channel TEXT NOT NULL,
    template TEXT NOT NULL,
    send_at TEXT NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS compliance_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    due_date TEXT NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS guest_bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    guest_name TEXT NOT NULL,
    check_in TEXT NOT NULL,
    check_out TEXT NOT NULL,
    payout REAL NOT NULL
);

CREATE VIEW IF NOT EXISTS rent_analytics AS
SELECT
    t.property_id,
    SUM(CASE WHEN r.status = 'paid' THEN r.amount ELSE 0 END) AS paid_amount,
    SUM(CASE WHEN r.status != 'paid' THEN r.amount ELSE 0 END) AS outstanding_amount
FROM tenants t
LEFT JOIN rent_invoices r ON r.tenant_id = t.id
GROUP BY t.property_id;
