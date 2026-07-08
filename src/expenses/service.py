from datetime import date
from venv import logger

from fastapi import HTTPException

from typing import List

from sqlmodel import select, desc, asc, func
from sqlmodel.ext.asyncio.session import AsyncSession

from src.expenses.models import Expense
from src.expenses.schemas import ExpenseCreate, Order, ExpenseQueryParams

from sqlalchemy.exc import SQLAlchemyError

async def create_expense(
    session: AsyncSession, expense: ExpenseCreate, user_id: int
) -> Expense:
    db_expense = Expense(**expense.model_dump(), user_id=user_id)
    session.add(db_expense)
    await session.commit()
    await session.refresh(db_expense)
    return db_expense


async def get_user_expenses(
    session: AsyncSession, user_id: int, filters: ExpenseQueryParams
) -> List[Expense]:
    query = select(Expense).where(Expense.user_id == user_id)

    if filters.category:
        query = query.where(Expense.category == filters.category)

    if filters.payment_method:
        query = query.where(Expense.payment_method == filters.payment_method)

    if filters.min_purchase is not None:
        query = query.where(Expense.amount >= filters.min_purchase)

    if filters.max_purchase is not None:
        query = query.where(Expense.amount <= filters.max_purchase)

    sort_column = getattr(Expense, filters.sort_by.value)

    if filters.order == Order.desc:
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    query = query.limit(filters.limit).offset(filters.offset)

    result = await session.execute(query)
    return result.scalars().all()


async def get_expense_by_id(session: AsyncSession, expense_id: int):
    return await session.get(Expense, expense_id)


async def update_expense(session: AsyncSession, expense: Expense, update_data: dict):
    for key, value in update_data.items():
        setattr(expense, key, value)

    session.add(expense)
    await session.commit()
    await session.refresh(expense)
    return expense


async def delete_expense(session: AsyncSession, expense: Expense) -> None:
    await session.delete(expense)
    await session.commit()

async def sum_expenses(session: AsyncSession,category:str | None, start_date: date | None, end_date: date | None, current_user_id: int):
    query = select(func.sum(Expense.amount)).where(Expense.user_id == current_user_id)

    if category:
        query = query.where(category == Expense.category)

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="Η αρχική ημερομηνία πρέπει να είναι πριν την τελική.",
        )

    if start_date:
        query = query.where(Expense.created_at >= start_date)

    if end_date:
        query = query.where(Expense.created_at <= end_date)

    try:
        result = await session.execute(query)

        total = result.scalar() or 0.0

        return {"total": total}

    except SQLAlchemyError as e:
        logger.error(f"Σφάλμα DB στον χρήστη {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Πρόβλημα επικοινωνίας με τη βάση δεδομένων."
        )