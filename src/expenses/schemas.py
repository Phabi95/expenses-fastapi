from pydantic import BaseModel, Field
from src.expenses.models import Category, PaymentMethod
from datetime import datetime
from typing import Optional
from enum import Enum
from fastapi import Query
from decimal import Decimal


class ExpenseBase(BaseModel):
    amount: Decimal = Field(
        description="Το ακριβές ποσό της συναλλαγής (π.χ. 45.50)",
        max_digits=10,
        decimal_places=2,
    )
    category: Category = Field(
        description="Τι αφορά το έξοδο (π.χ. Σούπερ Μάρκετ, Ενοίκιο)"
    )
    payment_method: PaymentMethod = Field(
        default=PaymentMethod.CARD,
        description="Αποδεκτές τιμές: card, cash, bank_transfer",
    )


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseResponse(ExpenseBase):
    id: int = Field(description="Το μοναδικό αναγνωριστικό του εξόδου στη βάση")
    created_at: datetime = Field(description="Ημερομηνία και ώρα δημιουργίας")
    updated_at: Optional[datetime] = Field(
        description="Ημερομηνία και ώρα τροποποίησης"
    )
    user_id: int = Field(description="Το ID του χρήστη που έκανε το έξοδο")


class ExpenseUpdate(BaseModel):
    category: Optional[Category] = None
    amount: Optional[Decimal] = None
    payment_method: Optional[PaymentMethod] = None


class Order(str, Enum):
    asc = "asc"
    desc = "desc"


class ExpenseSortField(str, Enum):
    created_at = "created_at"
    amount = "amount"
    category = "category"


class ExpenseQueryParams:
    def __init__(
        self,
        category: Optional[Category] = Query(
            None, description="Φιλτράρισμα ανά κατηγορία"
        ),
        payment_method: Optional[PaymentMethod] = Query(
            None, description="Φιλτράρισμα ανά τρόπο πληρωμής"
        ),
        min_purchase: Optional[Decimal] = Query(
            None, description="Ελάχιστο ποσό", precision=10, scale=2
        ),
        max_purchase: Optional[Decimal] = Query(
            None, description="Μέγιστο ποσό", precision=10, scale=2
        ),
        sort_by: ExpenseSortField = Query(
            ExpenseSortField.created_at, description="Πεδίο ταξινόμησης"
        ),
        order: Order = Query(Order.desc, description="Σειρά ταξινόμησης"),
        limit: int = Query(100, ge=1, le=100),
        offset: int = Query(0, ge=0),
    ):
        self.category = category
        self.payment_method = payment_method
        self.min_purchase = min_purchase
        self.max_purchase = max_purchase
        self.sort_by = sort_by
        self.order = order
        self.limit = limit
        self.offset = offset


class TotalExpense(BaseModel):
    total: Decimal
