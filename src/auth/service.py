from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.exceptions import EmailAlreadyExistsException, InvalidCredentialsException
from src.auth.models import User
from src.auth.repository import get_user_by_email, save_user
from src.auth.schemas import UserCreate
from src.auth.utils import create_access_token, get_password_hash, verify_password
from fastapi.security import OAuth2PasswordRequestForm

async def create_user(user_data: UserCreate, session: Session) -> User:
    if await get_user_by_email(session, user_data.email):
        raise EmailAlreadyExistsException()

    hashed_pw = get_password_hash(user_data.password)
    new_user = User(email=user_data.email, hashed_password=hashed_pw)

    return await save_user(session, new_user)


async def authenticate_user(
    form_data: OAuth2PasswordRequestForm, session: AsyncSession
) -> str:
    user = await get_user_by_email(session, form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise InvalidCredentialsException()

    return create_access_token(data={"sub": str(user.id), "role": user.role.value})
