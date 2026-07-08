from sqlmodel import Session, select
from src.auth.models import User

async def get_user_by_email(session: Session, email: str) -> User | None:
    result = await session.exec(select(User).where(User.email == email))
    return result.first()

async def save_user(session: Session, user: User) -> User:
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user