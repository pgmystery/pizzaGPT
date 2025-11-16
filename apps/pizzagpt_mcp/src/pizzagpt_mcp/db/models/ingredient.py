import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field


class Ingredient(SQLModel, table=True):
    __tablename__ = "ingredients"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False, index=True)
    name: str = Field(index=True, nullable=False, max_length=200, unique=True)
    cost_cents: int = Field(nullable=False, ge=0, description="Cost per unit in cents")
    is_available: bool = Field(default=True, nullable=False)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
