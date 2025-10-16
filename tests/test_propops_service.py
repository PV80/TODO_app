from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

from propops import PropOpsService


@pytest.fixture()
def service(tmp_path: Path) -> PropOpsService:
    db_path = tmp_path / "propops.db"
    return PropOpsService(db_path)


def test_property_tenant_and_invoice_flow(service: PropOpsService) -> None:
    property_ = service.add_property("Lavington Heights", "Long-term", "Nairobi", units=12)
    tenant = service.add_tenant(
        property_.id,
        "Amina Wanjiru",
        "+254700111222",
        lease_start=date(2024, 1, 1),
        lease_end=date(2024, 12, 31),
        monthly_rent=55000,
        is_airbnb=False,
    )
    invoice = service.create_rent_invoice(tenant.id, 55000, date(2024, 10, 1))

    outstanding = service.outstanding_invoices(date(2024, 10, 15))
    assert [inv.id for inv in outstanding] == [invoice.id]

    service.record_payment(invoice.id, date(2024, 10, 20))
    assert service.outstanding_invoices(date(2024, 10, 21)) == []

    summary = service.tenant_portfolio_summary()
    assert summary["tenants"] == 1
    assert summary["monthly_rent_roll"] == pytest.approx(55000)
    assert summary["outstanding"] == pytest.approx(0)


def test_maintenance_and_vendor_updates(service: PropOpsService) -> None:
    property_ = service.add_property("Nyali Villas", "Airbnb", "Mombasa", units=4)
    request = service.create_maintenance_request(property_.id, "Fix leaking tap", vendor="MajiFix")
    assert request.status == "open"

    updated = service.update_maintenance_status(request.id, "in-progress", vendor="MajiFix")
    assert updated.status == "in-progress"
    assert updated.vendor == "MajiFix"

    open_requests = service.open_requests()
    assert [req.id for req in open_requests] == [request.id]


def test_messaging_and_compliance_tracking(service: PropOpsService) -> None:
    send_at = datetime.now(timezone.utc) + timedelta(hours=1)
    message = service.schedule_message("+254712345678", "WhatsApp", "Rent due reminder", send_at)
    scheduled = service.list_messages()
    assert [msg.id for msg in scheduled] == [message.id]

    upcoming = service.messages_due_within(2)
    assert [msg.id for msg in upcoming] == [message.id]

    service.complete_message(message.id)
    assert service.messages_due_within(2) == []
    sent_messages = service.list_messages(status="sent")
    assert [msg.id for msg in sent_messages] == [message.id]

    task = service.add_compliance_task("File KRA landlord return", "KRA", date.today())
    due = service.due_compliance_tasks(date.today())
    assert [t.id for t in due] == [task.id]
    open_tasks = service.list_compliance_tasks()
    assert [t.id for t in open_tasks] == [task.id]

    service.update_compliance_status(task.id, "completed")
    assert service.list_compliance_tasks() == []
    completed = service.list_compliance_tasks(include_completed=True)
    assert [t.status for t in completed] == ["completed"]
