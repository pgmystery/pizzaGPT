from typing import Any, Dict, Optional
from sqlmodel import Session, select

from pizzagpt_mcp.db.database import get_engine, init_db
from pizzagpt_mcp.db.models import Customer
from pizzagpt_mcp.server import mcp


def _to_dict(c: Customer) -> Dict[str, Any]:
    return {
        "id": str(c.id),
        "name": c.name,
        "email": c.email,
        "phone": c.phone,
        "loyalty_points": c.loyalty_points,
    }


@mcp.tool(
    name="customers.find_or_create",
    description="Find an existing customer by email/phone/name or create one.",
)
def find_or_create(
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
) -> Dict[str, Any]:
    init_db()
    if not (name or email or phone):
        return {"ok": False, "error": "Provide at least one of name/email/phone"}
    with Session(get_engine()) as session:
        stmt = select(Customer)
        if email:
            stmt = stmt.where(Customer.email == email)
        elif phone:
            stmt = stmt.where(Customer.phone == phone)
        elif name:
            stmt = stmt.where(Customer.name == name)
        existing = session.exec(stmt.limit(1)).first()
        if existing:
            return {"ok": True, "customer": _to_dict(existing), "created": False}
        cust = Customer(name=name or (email or phone or "Guest"), email=email, phone=phone)
        session.add(cust)
        session.commit()
        session.refresh(cust)
        return {"ok": True, "customer": _to_dict(cust), "created": True}


@mcp.tool(
    name="customers.get",
    description="Get a customer by id (UUID).",
)
def get_customer(id: str) -> Dict[str, Any]:
    init_db()
    with Session(get_engine()) as session:
        c = session.get(Customer, id)
        if not c:
            return {"ok": False, "error": "customer not found"}
        return {"ok": True, "customer": _to_dict(c)}
