from typing import Any

from fastapi import APIRouter, Depends, Response, Body, BackgroundTasks, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.schemas import UserCreate, UserResponse, CreatePassword

from src.auth.service import create_user, authenticate_user
from src.database import SessionDep
from src.auth.dependencies import get_admin_user
from src.auth.repository import get_user_by_email
from datetime import datetime, timedelta, timezone
import jwt
from src.auth.utils import ALGORITHM
from src.config import settings
from src.auth.utils import get_password_hash
from src.auth.models import User

from src.email import send_reset_email


router = APIRouter(prefix="/auth", tags=["auth"])

admin_router = APIRouter(
    prefix="/admin", tags=["Admin"], dependencies=[Depends(get_admin_user)]
)

secret_key = settings.secret_key


@router.post("/register", response_model=UserResponse)
async def register(session: SessionDep, user: UserCreate):
    return await create_user(user, session)


@router.post("/login")
async def login(
    session: SessionDep,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> dict[str, Any]:

    access_token = await authenticate_user(form_data, session)

    user = await get_user_by_email(session=session, email=form_data.username)

    if not user:
        raise HTTPException(status_code=400, detail="Ο χρήστης δεν βρέθηκε")

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=False,
        secure=True,
        samesite="lax",
        max_age=1800,
    )

    response_data = {
        "message": "Επιτυχής σύνδεση",
        "user": {"id": user.id, "email": user.email},
    }
    return response_data


@admin_router.get("/dashboard")
async def get_dashboard():
    return {"message": "Πρόσβαση μόνο για διαχειριστές"}


@router.post("/forgot_password")
async def forgot_password(
    session: SessionDep, background_tasks: BackgroundTasks, email: str = Body(...)
):
    user = await get_user_by_email(session, email)

    if not user:
        return {"message": "Το email σταλθηκε επιτυχως,ελεγξε το email σου"}

    expire = datetime.now(timezone.utc) + timedelta(minutes=5)
    reset_token = jwt.encode(
        {"sub": str(user.id), "type": "reset", "exp": expire},
        secret_key,
        algorithm=ALGORITHM,
    )

    background_tasks.add_task(send_reset_email, email_to=user.email, token=reset_token)

    return {"message": "Εστάλησαν οδηγίες."}


@router.post("/reset_password")
async def reset_password(session: SessionDep, data: CreatePassword):
    try:
        payload = jwt.decode(data.token, secret_key, algorithms=[ALGORITHM])
        if payload.get("type") != "reset":
            raise InvalidTokenException()
        user_id = payload.get("sub")
    except jwt.PyJWTError:
        raise InvalidTokenException()

    user = await session.get(User, int(user_id))
    if not user:
        raise InvalidTokenException()

    user.hashed_password = get_password_hash(data.new_password)
    session.add(user)
    await session.commit()

    return {"message": "Ο κωδικός άλλαξε επιτυχώς."}
