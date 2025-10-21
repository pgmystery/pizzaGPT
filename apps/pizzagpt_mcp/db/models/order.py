import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERING = "delivering"
    COMPLETED = "completed"
    CANCELED = "canceled"


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False, index=True)
    customer_id: uuid.UUID = Field(foreign_key="customers.id", index=True, nullable=False)

    subtotal_cents: int = Field(default=0, ge=0, nullable=False)
    discount_cents: int = Field(default=0, ge=0, nullable=False)
    tax_cents: int = Field(default=0, ge=0, nullable=False)
    total_cents: int = Field(default=0, ge=0, nullable=False)

    status: OrderStatus = Field(default=OrderStatus.PENDING, nullable=False)
    notes: Optional[str] = Field(default=None, max_length=2000)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # relationships
    customer: "Customer" = Relationship(back_populates="orders")
    items: list["OrderItem"] = Relationship(back_populates="order")
