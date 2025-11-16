import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class MenuItem(SQLModel, table=True):
    __tablename__ = "menu_items"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False, index=True)
    name: str = Field(index=True, nullable=False, max_length=200)
    description: Optional[str] = Field(default=None, nullable=True, max_length=2000)
    size: Optional[str] = Field(default=None, nullable=True, max_length=50)  # e.g., small/medium/large or inches
    price_cents: int = Field(nullable=False, ge=0, description="Price in cents to avoid float issues")

    is_active: bool = Field(default=True, nullable=False)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # relationships
    order_items: list["OrderItem"] = Relationship(back_populates="menu_item")
