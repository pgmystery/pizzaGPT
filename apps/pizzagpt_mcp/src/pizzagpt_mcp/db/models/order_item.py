import uuid
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False, index=True)

    order_id: uuid.UUID = Field(foreign_key="orders.id", index=True, nullable=False)
    menu_item_id: uuid.UUID = Field(foreign_key="menu_items.id", index=True, nullable=False)

    quantity: int = Field(default=1, ge=1, nullable=False)
    special_requests: Optional[str] = Field(default=None, max_length=2000)

    line_total_cents: int = Field(default=0, ge=0, nullable=False, description="Cached line total for this item")

    # relationships
    order: "Order" = Relationship(back_populates="items")
    menu_item: "MenuItem" = Relationship(back_populates="order_items")
