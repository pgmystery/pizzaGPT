from typing import Any, Dict, Optional
from sqlmodel import Session, select

from pizzagpt_mcp.db.database import get_engine, init_db
from pizzagpt_mcp.db.models import MenuItem
from pizzagpt_mcp.server import mcp


def _to_dict(mi: MenuItem) -> Dict[str, Any]:
    return {
        "id": str(mi.id),
        "name": mi.name,
        "description": mi.description,
        "size": mi.size,
        "price_cents": mi.price_cents,
        "is_active": mi.is_active,
    }


@mcp.tool(
    name="menu.list_items",
    description="List menu items with optional filters: name (substring), only_active (default true).",
)
def list_items(name: Optional[str] = None, only_active: bool = True) -> Dict[str, Any]:
    init_db()
    with Session(get_engine()) as session:
        stmt = select(MenuItem)
        if only_active:
            stmt = stmt.where(MenuItem.is_active == True)  # noqa: E712
        if name:
            stmt = stmt.where(MenuItem.name.ilike(f"%{name}%"))
        items = session.exec(stmt.order_by(MenuItem.name, MenuItem.size)).all()
        return {"ok": True, "items": [_to_dict(i) for i in items]}


@mcp.tool(
    name="menu.get_item",
    description="Get a single menu item by id (UUID).",
)
def get_item(id: str) -> Dict[str, Any]:
    init_db()
    with Session(get_engine()) as session:
        mi = session.get(MenuItem, id)
        if not mi:
            return {"ok": False, "error": "menu item not found"}
        return {"ok": True, "item": _to_dict(mi)}
