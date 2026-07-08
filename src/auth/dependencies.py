from fastapi import Cookie

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
import jwt
from src.auth.utils import ALGORITHM
from src.config import settings
from src.auth.exceptions import (
    InvalidTokenException,
    TokenExpiredException,
    AdminAccessDenied,
)
from src.auth.schemas import TokenUser
from src.auth.models import Role

secret_key = settings.secret_key


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(access_token: str = Cookie(default=None)) -> TokenUser:
    if access_token is None:
        raise InvalidTokenException()
    try:
        payload = jwt.decode(access_token, secret_key, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role_str: str = payload.get("role")

        if user_id is None or role_str is None:
            raise InvalidTokenException()

        return TokenUser(id=int(user_id), role=Role(role_str))

    except jwt.ExpiredSignatureError:
        raise TokenExpiredException()
    except jwt.InvalidTokenError:
        raise InvalidTokenException()


def get_admin_user(current_user: TokenUser = Depends(get_current_user)) -> TokenUser:
    if current_user.role != Role.admin:
        raise AdminAccessDenied()
    return current_user
