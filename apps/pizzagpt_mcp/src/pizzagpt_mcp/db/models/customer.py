import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Customer(SQLModel, table=True):
    __tablename__ = "customers"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False, index=True)
    name: str = Field(nullable=False, max_length=200, index=True)
    email: Optional[str] = Field(default=None, max_length=320, index=True)
    phone: Optional[str] = Field(default=None, max_length=32, index=True)
    loyalty_points: int = Field(default=0, ge=0, nullable=False)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # relationships
    orders: list["Order"] = Relationship(back_populates="customer")
