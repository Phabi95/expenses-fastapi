from sqlmodel import SQLModel, Field
from datetime import date, datetime, timezone
from sqlalchemy import Column, DateTime, Numeric
from typing import Optional
from enum import Enum
from decimal import Decimal


class PaymentMethod(str, Enum):
    CARD = "card"
    CASH = "cash"
    BANK_transfer = "bank_transfer"


class Category(str, Enum):
    SUPERMARKET = "supermarket"
    RENT = "rent"
    UTILITIES = "utilities"
    ENTERTAINMENT = "entertainment"
    TRANSPORTATION = "transportation"
    OTHER = "other"


class Expense(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: Decimal = Field(default=0.0, sa_column=Column(Numeric(10, 2)))
    category: Category = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc)
        ),
    )
    payment_method: PaymentMethod = Field(default=PaymentMethod.CARD)
    user_id: int = Field(foreign_key="user.id")
