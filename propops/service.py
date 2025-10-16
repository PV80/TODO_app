"""Business logic for the PropOps AI MVP."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, List, Optional
import sqlite3

from .database import get_connection, initialize_database


@dataclass
class Property:
    id: int
    name: str
    category: str
    location: str
    units: int


@dataclass
class Tenant:
    id: int
    property_id: int
    full_name: str
    contact: str
    lease_start: date
    lease_end: Optional[date]
    monthly_rent: float
    is_airbnb: bool


@dataclass
class RentInvoice:
    id: int
    tenant_id: int
    amount: float
    due_date: date
    status: str
    paid_date: Optional[date]


@dataclass
class MaintenanceRequest:
    id: int
    property_id: int
    description: str
    status: str
    vendor: Optional[str]
    created_at: datetime
    updated_at: datetime


@dataclass
class ComplianceTask:
    id: int
    title: str
    category: str
    due_date: date
    status: str


@dataclass
class ScheduledMessage:
    id: int
    recipient: str
    channel: str
    template: str
    send_at: datetime
    status: str


class PropOpsService:
    """High-level facade wrapping the SQLite data store."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        initialize_database(db_path)

    # ------------------------------------------------------------------
    # Property and tenant management
    # ------------------------------------------------------------------
    def add_property(
        self, name: str, category: str, location: str, units: int = 1
    ) -> Property:
        with get_connection(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO properties(name, category, location, units)
                VALUES (?, ?, ?, ?)
                RETURNING id, name, category, location, units
                """,
                (name, category, location, units),
            )
            row = cursor.fetchone()
        return Property(**row)

    def list_properties(self) -> List[Property]:
        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                "SELECT id, name, category, location, units FROM properties"
            ).fetchall()
        return [Property(**row) for row in rows]

    def add_tenant(
        self,
        property_id: int,
        full_name: str,
        contact: str,
        lease_start: date,
        lease_end: Optional[date],
        monthly_rent: float,
        is_airbnb: bool = False,
    ) -> Tenant:
        with get_connection(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO tenants(
                    property_id, full_name, contact, lease_start, lease_end,
                    monthly_rent, is_airbnb
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                RETURNING id, property_id, full_name, contact, lease_start,
                    lease_end, monthly_rent, is_airbnb
                """,
                (
                    property_id,
                    full_name,
                    contact,
                    lease_start.isoformat(),
                    lease_end.isoformat() if lease_end else None,
                    monthly_rent,
                    int(is_airbnb),
                ),
            )
            row = cursor.fetchone()
        return Tenant(
            id=row["id"],
            property_id=row["property_id"],
            full_name=row["full_name"],
            contact=row["contact"],
            lease_start=date.fromisoformat(row["lease_start"]),
            lease_end=date.fromisoformat(row["lease_end"]) if row["lease_end"] else None,
            monthly_rent=row["monthly_rent"],
            is_airbnb=bool(row["is_airbnb"]),
        )

    def list_tenants(self, property_id: Optional[int] = None) -> List[Tenant]:
        query = "SELECT * FROM tenants"
        params: Iterable[object] = ()
        if property_id is not None:
            query += " WHERE property_id = ?"
            params = (property_id,)
        with get_connection(self.db_path) as conn:
            rows = conn.execute(query, params).fetchall()
        tenants = []
        for row in rows:
            tenants.append(
                Tenant(
                    id=row["id"],
                    property_id=row["property_id"],
                    full_name=row["full_name"],
                    contact=row["contact"],
                    lease_start=date.fromisoformat(row["lease_start"]),
                    lease_end=date.fromisoformat(row["lease_end"])
                    if row["lease_end"]
                    else None,
                    monthly_rent=row["monthly_rent"],
                    is_airbnb=bool(row["is_airbnb"]),
                )
            )
        return tenants

    # ------------------------------------------------------------------
    # Rent management
    # ------------------------------------------------------------------
    def create_rent_invoice(
        self, tenant_id: int, amount: float, due_date: date
    ) -> RentInvoice:
        with get_connection(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO rent_invoices(tenant_id, amount, due_date, status)
                VALUES (?, ?, ?, 'pending')
                RETURNING id, tenant_id, amount, due_date, status, paid_date
                """,
                (tenant_id, amount, due_date.isoformat()),
            )
            row = cursor.fetchone()
        return self._map_invoice(row)

    def record_payment(self, invoice_id: int, paid_date: date) -> RentInvoice:
        with get_connection(self.db_path) as conn:
            cursor = conn.execute(
                """
                UPDATE rent_invoices
                SET status = 'paid', paid_date = ?
                WHERE id = ?
                RETURNING id, tenant_id, amount, due_date, status, paid_date
                """,
                (paid_date.isoformat(), invoice_id),
            )
            row = cursor.fetchone()
            if row is None:
                raise ValueError("Invoice not found")
        return self._map_invoice(row)

    def outstanding_invoices(self, reference_date: Optional[date] = None) -> List[RentInvoice]:
        ref = reference_date or date.today()
        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT * FROM rent_invoices
                WHERE status != 'paid' AND due_date <= ?
                ORDER BY due_date
                """,
                (ref.isoformat(),),
            ).fetchall()
        return [self._map_invoice(row) for row in rows]

    # ------------------------------------------------------------------
    # Maintenance & vendor coordination
    # ------------------------------------------------------------------
    def create_maintenance_request(
        self, property_id: int, description: str, vendor: Optional[str] = None
    ) -> MaintenanceRequest:
        now = datetime.now(timezone.utc)
        with get_connection(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO maintenance_requests(
                    property_id, description, status, vendor, created_at, updated_at
                )
                VALUES (?, ?, 'open', ?, ?, ?)
                RETURNING *
                """,
                (
                    property_id,
                    description,
                    vendor,
                    now.isoformat(timespec="seconds"),
                    now.isoformat(timespec="seconds"),
                ),
            )
            row = cursor.fetchone()
        return self._map_request(row)

    def update_maintenance_status(
        self, request_id: int, status: str, vendor: Optional[str] = None
    ) -> MaintenanceRequest:
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with get_connection(self.db_path) as conn:
            cursor = conn.execute(
                """
                UPDATE maintenance_requests
                SET status = ?, vendor = COALESCE(?, vendor), updated_at = ?
                WHERE id = ?
                RETURNING *
                """,
                (status, vendor, now, request_id),
            )
            row = cursor.fetchone()
            if row is None:
                raise ValueError("Maintenance request not found")
        return self._map_request(row)

    def open_requests(self) -> List[MaintenanceRequest]:
        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM maintenance_requests WHERE status != 'closed'"
            ).fetchall()
        return [self._map_request(row) for row in rows]

    # ------------------------------------------------------------------
    # Messaging & compliance automation
    # ------------------------------------------------------------------
    def schedule_message(
        self, recipient: str, channel: str, template: str, send_at: datetime
    ) -> ScheduledMessage:
        with get_connection(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO scheduled_messages(recipient, channel, template, send_at, status)
                VALUES (?, ?, ?, ?, 'pending')
                RETURNING *
                """,
                (recipient, channel, template, send_at.isoformat(timespec="seconds")),
            )
            row = cursor.fetchone()
        return self._map_message(row)

    def messages_due_within(self, hours: int) -> List[ScheduledMessage]:
        horizon = datetime.now(timezone.utc) + timedelta(hours=hours)
        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT * FROM scheduled_messages
                WHERE status = 'pending' AND send_at <= ?
                ORDER BY send_at
                """,
                (horizon.isoformat(timespec="seconds"),),
            ).fetchall()
        return [self._map_message(row) for row in rows]

    def complete_message(self, message_id: int) -> ScheduledMessage:
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with get_connection(self.db_path) as conn:
            cursor = conn.execute(
                """
                UPDATE scheduled_messages
                SET status = 'sent', send_at = ?
                WHERE id = ?
                RETURNING *
                """,
                (now, message_id),
            )
            row = cursor.fetchone()
            if row is None:
                raise ValueError("Message not found")
        return self._map_message(row)

    def add_compliance_task(
        self, title: str, category: str, due_date: date
    ) -> ComplianceTask:
        with get_connection(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO compliance_tasks(title, category, due_date, status)
                VALUES (?, ?, ?, 'open')
                RETURNING *
                """,
                (title, category, due_date.isoformat()),
            )
            row = cursor.fetchone()
        return self._map_task(row)

    def due_compliance_tasks(self, reference_date: Optional[date] = None) -> List[ComplianceTask]:
        ref = reference_date or date.today()
        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT * FROM compliance_tasks
                WHERE status != 'completed' AND due_date <= ?
                ORDER BY due_date
                """,
                (ref.isoformat(),),
            ).fetchall()
        return [self._map_task(row) for row in rows]

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------
    def tenant_portfolio_summary(self) -> dict:
        with get_connection(self.db_path) as conn:
            totals = conn.execute(
                """
                SELECT
                    COUNT(*) AS tenant_count,
                    SUM(monthly_rent) AS monthly_rent_roll,
                    SUM(CASE WHEN is_airbnb = 1 THEN 1 ELSE 0 END) AS airbnb_units
                FROM tenants
                """
            ).fetchone()
            arrears = conn.execute(
                """
                SELECT SUM(amount) AS overdue
                FROM rent_invoices
                WHERE status != 'paid'
                """
            ).fetchone()
        return {
            "tenants": totals["tenant_count"] or 0,
            "monthly_rent_roll": totals["monthly_rent_roll"] or 0.0,
            "airbnb_units": totals["airbnb_units"] or 0,
            "outstanding": arrears["overdue"] or 0.0,
        }

    # ------------------------------------------------------------------
    # Mapping helpers
    # ------------------------------------------------------------------
    def _map_invoice(self, row: sqlite3.Row) -> RentInvoice:
        return RentInvoice(
            id=row["id"],
            tenant_id=row["tenant_id"],
            amount=row["amount"],
            due_date=date.fromisoformat(row["due_date"]),
            status=row["status"],
            paid_date=date.fromisoformat(row["paid_date"])
            if row["paid_date"]
            else None,
        )

    def _map_request(self, row: sqlite3.Row) -> MaintenanceRequest:
        return MaintenanceRequest(
            id=row["id"],
            property_id=row["property_id"],
            description=row["description"],
            status=row["status"],
            vendor=row["vendor"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def _map_task(self, row: sqlite3.Row) -> ComplianceTask:
        return ComplianceTask(
            id=row["id"],
            title=row["title"],
            category=row["category"],
            due_date=date.fromisoformat(row["due_date"]),
            status=row["status"],
        )

    def _map_message(self, row: sqlite3.Row) -> ScheduledMessage:
        return ScheduledMessage(
            id=row["id"],
            recipient=row["recipient"],
            channel=row["channel"],
            template=row["template"],
            send_at=datetime.fromisoformat(row["send_at"]),
            status=row["status"],
        )

    # ------------------------------------------------------------------
    # Utilities for serialising dataclasses
    # ------------------------------------------------------------------
    @staticmethod
    def to_dict(obj) -> dict:
        if hasattr(obj, "__dict__"):
            data = asdict(obj)
            for key, value in list(data.items()):
                if isinstance(value, (date, datetime)):
                    data[key] = value.isoformat()
            return data
        raise TypeError(f"Object {obj!r} is not serialisable")
