# PropOps AI (Kenya Edition)

PropOps AI is a lightweight prototype for automating operations for Kenyan
landlords and Airbnb hosts. The project demonstrates how Python, SQL and Java
can work together to cover the core MVP modules: property dashboards, rent
collection, tenant CRM, automated messaging, and compliance reminders.

## Repository layout

```
propops/                 # Python service layer and database helpers
sql/propops_schema.sql   # SQLite schema capturing the data model
java_client/             # Java console utility for basic portfolio reports
```

Additional background information is available in
[`docs/propops_ai_plan.md`](docs/propops_ai_plan.md).

## Python service

The Python package exposes a `PropOpsService` facade that wraps an SQLite
database. It offers helper methods to:

- register properties and tenants (long-term and Airbnb)
- issue rent invoices, capture payments, and list outstanding arrears
- store maintenance requests and coordinate vendor updates
- schedule outbound WhatsApp/SMS reminders and mark them as sent
- maintain compliance obligations with due-date tracking
- compute small portfolio summaries for dashboards

### Quick start

```bash
python -m pip install -r requirements.txt
python - <<'PY'
from datetime import date
from pathlib import Path
from propops import PropOpsService

service = PropOpsService(Path('propops_demo.db'))
property_ = service.add_property('Kilimani Suites', 'Airbnb', 'Nairobi', units=6)
tenant = service.add_tenant(
    property_.id,
    'John Mwangi',
    '+254700000000',
    lease_start=date(2024, 1, 1),
    lease_end=None,
    monthly_rent=65000,
    is_airbnb=False,
)
invoice = service.create_rent_invoice(tenant.id, 65000, date(2024, 10, 1))
print(service.tenant_portfolio_summary())
PY
```

The service automatically initialises the SQLite schema. Data is stored in the
provided database path.

## SQL schema

The `sql/propops_schema.sql` file defines the persistence layer. It includes
entities for properties, tenants, invoices, maintenance requests, scheduled
messages, compliance tasks, and Airbnb guest bookings. It can be executed using
any SQLite client:

```bash
sqlite3 propops_demo.db < sql/propops_schema.sql
```

## Java console client

The `java_client` folder contains a tiny console application that demonstrates
how a Java team member could generate roll-up reports from the PropOps
database. It uses JDBC to query the same SQLite database created by the Python
service and prints property-level revenue and arrears.

Compile and run with:

```bash
cd java_client
javac -cp lib/sqlite-jdbc.jar src/main/java/propops/PortfolioReporter.java
java -cp lib/sqlite-jdbc.jar:src/main/java propops.PortfolioReporter ../propops_demo.db
```

(Any SQLite JDBC driver JAR may be dropped into `java_client/lib`.)

## Tests

A small pytest suite exercises the Python façade. Run it with:

```bash
pytest
```
