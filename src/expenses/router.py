from fastapi import APIRouter, Depends, status, Query
from typing import Annotated
from sqlmodel import select, func


from log import logger


from src.expenses.models import Expense
from src.expenses.schemas import (
    ExpenseCreate,
    ExpenseResponse,
    ExpenseUpdate,
    ExpenseQueryParams,
    TotalExpense,
)

from src.expenses import service
from src.auth.dependencies import get_current_user
from src.database import SessionDep
from src.expenses.dependencies import get_valid_expense

from datetime import date
from src.auth.schemas import TokenUser


router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post("/", response_model=ExpenseResponse)
async def create_expenses(
    expense: ExpenseCreate,
    session: SessionDep,
    current_user: TokenUser = Depends(get_current_user),
) -> Expense:
    return await service.create_expense(session, expense, current_user.id)


@router.get("/", response_model=list[ExpenseResponse])
async def read_expenses(
    session: SessionDep,
    filters: ExpenseQueryParams = Depends(),
    current_user: TokenUser = Depends(get_current_user),
) -> list[Expense]:
    return await service.get_user_expenses(session, current_user.id, filters)


@router.patch("/{expense_id}", response_model=ExpenseResponse)
async def update(
    session: SessionDep,
    expense_update: ExpenseUpdate,
    expense: Expense = Depends(get_valid_expense),
):

    update_data = expense_update.model_dump(exclude_unset=True)
    return await service.update_expense(session, expense, update_data)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense_endpoint(
    session: SessionDep, expense: Expense = Depends(get_valid_expense)
):
    await service.delete_expense(session, expense)


@router.get("/Purchases", response_model=TotalExpense)
async def summary_expenses(
    session: SessionDep,
    category: Annotated[str | None, Query()] = None,
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
    current_user: TokenUser = Depends(get_current_user),
):
    return await service.sum_expenses(session, category, start_date, end_date, current_user.id)


@router.get("/{expense_id}", response_model=ExpenseResponse)
async def read_expense(expense: Expense = Depends(get_valid_expense)):
    return expense
