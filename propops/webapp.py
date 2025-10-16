
"""Flask web interface for PropOps AI."""

from __future__ import annotations

import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from flask import Flask, flash, redirect, render_template, request, url_for

from .service import PropOpsService


def create_app(db_path: Optional[Path | str] = None) -> Flask:
    """Create and configure the PropOps web application."""

    app = Flask(
        __name__,
        template_folder=str(Path(__file__).parent / "templates"),
        static_folder=str(Path(__file__).parent / "static"),
    )
    app.config["SECRET_KEY"] = os.environ.get("PROPOPS_SECRET_KEY", "propops-dev")

    database_path = Path(db_path or os.environ.get("PROPOPS_DB", "propops_ui.db"))
    service = PropOpsService(database_path)

    if os.environ.get("PROPOPS_SEED_DEMO", "1") != "0":
        _seed_demo_data(service)

    @app.context_processor
    def inject_globals():
        return {"app_name": "PropOps AI"}

    @app.route("/")
    def dashboard():
        summary = service.tenant_portfolio_summary()
        properties = service.list_properties()
        tenants = service.list_tenants()
        invoices = service.outstanding_invoices()
        maintenance = service.open_requests()
        compliance = service.list_compliance_tasks()
        messages = service.list_messages(limit=10)
        tenant_lookup = {tenant.id: tenant for tenant in tenants}
        return render_template(
            "dashboard.html",
            summary=summary,
            properties=properties,
            tenants=tenants,
            invoices=invoices,
            maintenance=maintenance,
            compliance=compliance,
            messages=messages,
            tenant_lookup=tenant_lookup,
        )

    @app.post("/properties")
    def create_property():
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        location = request.form.get("location", "").strip()
        units_raw = request.form.get("units", "1")
        if not name or not category or not location:
            flash("Property name, category, and location are required.", "error")
            return redirect(url_for("dashboard"))
        try:
            units = int(units_raw)
        except ValueError:
            flash("Units must be a whole number.", "error")
            return redirect(url_for("dashboard"))
        service.add_property(name, category, location, units=units)
        flash("Property added successfully.", "success")
        return redirect(url_for("dashboard"))

    @app.post("/tenants")
    def create_tenant():
        property_id_raw = request.form.get("property_id")
        full_name = request.form.get("full_name", "").strip()
        contact = request.form.get("contact", "").strip()
        lease_start_raw = request.form.get("lease_start", "").strip()
        lease_end_raw = request.form.get("lease_end", "").strip()
        monthly_rent_raw = request.form.get("monthly_rent", "").strip()
        is_airbnb = request.form.get("is_airbnb") == "on"

        if not property_id_raw or not full_name or not contact or not lease_start_raw:
            flash("All tenant fields except lease end are required.", "error")
            return redirect(url_for("dashboard"))

        try:
            property_id = int(property_id_raw)
            lease_start = date.fromisoformat(lease_start_raw)
            lease_end = date.fromisoformat(lease_end_raw) if lease_end_raw else None
            monthly_rent = float(monthly_rent_raw)
        except ValueError:
            flash("Check the tenant details – dates and rent must be valid numbers.", "error")
            return redirect(url_for("dashboard"))

        service.add_tenant(
            property_id,
            full_name,
            contact,
            lease_start=lease_start,
            lease_end=lease_end,
            monthly_rent=monthly_rent,
            is_airbnb=is_airbnb,
        )
        flash("Tenant saved successfully.", "success")
        return redirect(url_for("dashboard"))

    @app.post("/invoices")
    def create_invoice():
        tenant_id_raw = request.form.get("tenant_id")
        amount_raw = request.form.get("amount", "").strip()
        due_date_raw = request.form.get("due_date", "").strip()

        if not tenant_id_raw or not amount_raw or not due_date_raw:
            flash("Tenant, amount, and due date are required for invoices.", "error")
            return redirect(url_for("dashboard"))

        try:
            tenant_id = int(tenant_id_raw)
            amount = float(amount_raw)
            due_date = date.fromisoformat(due_date_raw)
        except ValueError:
            flash("Please provide valid numbers for tenant and amount, and a correct date.", "error")
            return redirect(url_for("dashboard"))

        service.create_rent_invoice(tenant_id, amount, due_date)
        flash("Invoice created successfully.", "success")
        return redirect(url_for("dashboard"))

    @app.post("/invoices/<int:invoice_id>/pay")
    def mark_invoice_paid(invoice_id: int):
        service.record_payment(invoice_id, date.today())
        flash("Invoice marked as paid.", "success")
        return redirect(url_for("dashboard"))

    @app.post("/maintenance")
    def create_maintenance():
        property_id_raw = request.form.get("property_id")
        description = request.form.get("description", "").strip()
        vendor = request.form.get("vendor", "").strip() or None
        if not property_id_raw or not description:
            flash("Property and description are required for maintenance.", "error")
            return redirect(url_for("dashboard"))
        try:
            property_id = int(property_id_raw)
        except ValueError:
            flash("Invalid property selected for maintenance.", "error")
            return redirect(url_for("dashboard"))
        service.create_maintenance_request(property_id, description, vendor=vendor)
        flash("Maintenance request logged.", "success")
        return redirect(url_for("dashboard"))

    @app.post("/maintenance/<int:request_id>/close")
    def close_maintenance(request_id: int):
        service.update_maintenance_status(request_id, "closed")
        flash("Maintenance request closed.", "success")
        return redirect(url_for("dashboard"))

    @app.post("/compliance")
    def create_compliance():
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        due_date_raw = request.form.get("due_date", "").strip()
        if not title or not category or not due_date_raw:
            flash("Title, category, and due date are required for compliance tasks.", "error")
            return redirect(url_for("dashboard"))
        try:
            due_date = date.fromisoformat(due_date_raw)
        except ValueError:
            flash("Invalid date for compliance task.", "error")
            return redirect(url_for("dashboard"))
        service.add_compliance_task(title, category, due_date)
        flash("Compliance reminder added.", "success")
        return redirect(url_for("dashboard"))

    @app.post("/compliance/<int:task_id>/complete")
    def complete_compliance(task_id: int):
        service.update_compliance_status(task_id, "completed")
        flash("Compliance task completed.", "success")
        return redirect(url_for("dashboard"))

    @app.post("/messages")
    def schedule_message():
        recipient = request.form.get("recipient", "").strip()
        channel = request.form.get("channel", "").strip()
        template = request.form.get("template", "").strip()
        send_at_raw = request.form.get("send_at", "").strip()
        if not recipient or not channel or not template or not send_at_raw:
            flash("All messaging fields are required.", "error")
            return redirect(url_for("dashboard"))
        try:
            send_at = datetime.fromisoformat(send_at_raw)
            if send_at.tzinfo is None:
                send_at = send_at.replace(tzinfo=timezone.utc)
        except ValueError:
            flash("Invalid schedule date/time for message.", "error")
            return redirect(url_for("dashboard"))
        service.schedule_message(recipient, channel, template, send_at)
        flash("Message scheduled.", "success")
        return redirect(url_for("dashboard"))

    return app


def _seed_demo_data(service: PropOpsService) -> None:
    if service.list_properties():
        return

    kilimani = service.add_property("Kilimani Suites", "Airbnb", "Nairobi", units=6)
    lavington = service.add_property("Lavington Heights", "Long-term", "Nairobi", units=12)

    alice = service.add_tenant(
        kilimani.id,
        "Alice Naliaka",
        "+254712345678",
        lease_start=date(2024, 1, 10),
        lease_end=None,
        monthly_rent=72000,
        is_airbnb=True,
    )
    brian = service.add_tenant(
        lavington.id,
        "Brian Kimani",
        "+254733222111",
        lease_start=date(2023, 6, 1),
        lease_end=None,
        monthly_rent=65000,
        is_airbnb=False,
    )

    today = date.today()
    service.create_rent_invoice(alice.id, 72000, today.replace(day=1))
    service.create_rent_invoice(brian.id, 65000, today.replace(day=5))

    service.create_maintenance_request(kilimani.id, "Deep clean apartment 3A", vendor="Sparkle Squad")
    service.add_compliance_task("File KRA rental income return", "KRA", today + timedelta(days=7))
    service.schedule_message(
        "+254712345678",
        "WhatsApp",
        "Remember to settle October rent",
        datetime.now(timezone.utc) + timedelta(hours=6),
    )


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
