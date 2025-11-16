import uuid
from typing import Any, Dict, List, Optional
from sqlmodel import Session, select

from pizzagpt_mcp.db.database import get_engine, init_db
from pizzagpt_mcp.db.models import Customer, MenuItem, Order, OrderItem, OrderStatus
from pizzagpt_mcp.server import mcp


def _order_item_dict(oi: OrderItem) -> Dict[str, Any]:
    return {
        "id": str(oi.id),
        "menu_item_id": str(oi.menu_item_id),
        "quantity": oi.quantity,
        "special_requests": oi.special_requests,
        "line_total_cents": oi.line_total_cents,
    }


def _order_dict(o: Order) -> Dict[str, Any]:
    return {
        "id": str(o.id),
        "customer_id": str(o.customer_id),
        "subtotal_cents": o.subtotal_cents,
        "discount_cents": o.discount_cents,
        "tax_cents": o.tax_cents,
        "total_cents": o.total_cents,
        "status": o.status.value if hasattr(o.status, "value") else str(o.status),
        "notes": o.notes,
        "items": [_order_item_dict(i) for i in (o.items or [])],
    }


def _recalculate_totals(session: Session, order: Order) -> None:
    subtotal = 0
    for it in order.items:
        mi = session.get(MenuItem, it.menu_item_id)
        price = mi.price_cents if mi else 0
        it.line_total_cents = price * it.quantity
        subtotal += it.line_total_cents
    order.subtotal_cents = subtotal
    taxable = max(0, order.subtotal_cents - order.discount_cents)
    order.tax_cents = int(round(taxable * 0.08))
    order.total_cents = order.subtotal_cents - order.discount_cents + order.tax_cents


@mcp.tool(
    name="orders.create",
    description="Create an order: customer_id, items[{menu_item_id, quantity, special_requests?}], notes?, discount_cents?",
)
def create_order(
        customer_id: str,
        items: List[Dict[str, Any]],
        notes: Optional[str] = None,
        discount_cents: int = 0,
) -> Dict[str, Any]:
    init_db()
    if not items:
        return {"ok": False, "error": "items list is required"}
    with Session(get_engine()) as session:
        cust = session.get(Customer, customer_id)
        if not cust:
            return {"ok": False, "error": "customer not found"}
        order = Order(customer_id=cust.id, status=OrderStatus.PENDING, notes=notes, discount_cents=int(discount_cents))
        session.add(order)
        session.flush()

        order_items: List[OrderItem] = []
        for row in items:
            mid = row.get("menu_item_id")
            qty = int(row.get("quantity", 1))
            if not mid or qty < 1:
                return {"ok": False, "error": "each item requires menu_item_id and quantity>=1"}
            if not session.get(MenuItem, mid):
                return {"ok": False, "error": f"menu item not found: {mid}"}
            oi = OrderItem(
                order_id=order.id,
                menu_item_id=uuid.UUID(str(mid)),
                quantity=qty,
                special_requests=row.get("special_requests"),
            )
            order_items.append(oi)
            session.add(oi)

        session.flush()
        order.items = order_items
        _recalculate_totals(session, order)
        session.add(order)
        session.commit()
        session.refresh(order)
        return {"ok": True, "order": _order_dict(order)}


@mcp.tool(
    name="orders.add_item",
    description="Add an item to an order: order_id, menu_item_id, quantity>=1, special_requests?",
)
def add_item(
        order_id: str,
        menu_item_id: str,
        quantity: int = 1,
        special_requests: Optional[str] = None,
) -> Dict[str, Any]:
    init_db()
    if quantity < 1:
        return {"ok": False, "error": "quantity must be >= 1"}
    with Session(get_engine()) as session:
        order = session.get(Order, order_id)
        if not order:
            return {"ok": False, "error": "order not found"}
        if session.get(MenuItem, menu_item_id) is None:
            return {"ok": False, "error": "menu item not found"}
        oi = OrderItem(
            order_id=order.id,
            menu_item_id=uuid.UUID(str(menu_item_id)),
            quantity=int(quantity),
            special_requests=special_requests,
        )
        session.add(oi)
        session.flush()
        session.refresh(order)
        _recalculate_totals(session, order)
        session.add(order)
        session.commit()
        session.refresh(order)
        return {"ok": True, "order": _order_dict(order)}


@mcp.tool(
    name="orders.set_status",
    description="Update order status: order_id, status in [pending, confirmed, preparing, ready, delivering, completed, canceled].",
)
def set_status(order_id: str, status: str) -> Dict[str, Any]:
    init_db()
    try:
        s = OrderStatus(status)
    except Exception:
        return {"ok": False, "error": f"invalid status: {status}"}
    with Session(get_engine()) as session:
        order = session.get(Order, order_id)
        if not order:
            return {"ok": False, "error": "order not found"}
        order.status = s
        session.add(order)
        session.commit()
        session.refresh(order)
        return {"ok": True, "order": _order_dict(order)}


@mcp.tool(
    name="orders.get",
    description="Get an order by id.",
)
def get_order(id: str) -> Dict[str, Any]:
    init_db()
    with Session(get_engine()) as session:
        order = session.get(Order, id)
        if not order:
            return {"ok": False, "error": "order not found"}
        order.items  # touch relationship
        return {"ok": True, "order": _order_dict(order)}


@mcp.tool(
    name="orders.list",
    description="List orders, optionally filtered by customer_id and/or status; limit defaults to 50.",
)
def list_orders(
        customer_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
) -> Dict[str, Any]:
    init_db()
    with Session(get_engine()) as session:
        stmt = select(Order)
        if customer_id:
            stmt = stmt.where(Order.customer_id == uuid.UUID(str(customer_id)))
        if status:
            try:
                s = OrderStatus(status)
            except Exception:
                return {"ok": False, "error": f"invalid status: {status}"}
            stmt = stmt.where(Order.status == s)
        orders = session.exec(stmt.order_by(Order.created_at.desc()).limit(int(limit))).all()
        for o in orders:
            o.items
        return {"ok": True, "orders": [_order_dict(o) for o in orders]}
