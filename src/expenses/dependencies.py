from fastapi import Depends, Query
from typing import Optional

from src.database import SessionDep

from src.expenses.exceptions import ExpenseNotFound, ExpenseAccessDenied
from src.expenses.models import Expense
from src.expenses import service
from src.expenses.service import get_expense_by_id
from src.expenses.schemas import Order, ExpenseSortField

from src.auth.dependencies import get_current_user
from src.auth.schemas import TokenUser


async def get_valid_expense(
    expense_id: int,
    session: SessionDep,
    current_user: TokenUser = Depends(get_current_user),
) -> Expense:
    expense = await service.get_expense_by_id(session, expense_id)

    if not expense:
        raise ExpenseNotFound()

    
    if expense.user_id != current_user.id:
        raise ExpenseAccessDenied()

    return expense
