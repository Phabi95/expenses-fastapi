from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from src.config import settings
from src.auth.constants import ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

password_hash = PasswordHash.recommended()
secret_key = settings.secret_key


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_pw: str) -> bool:
    return password_hash.verify(plain_password, hashed_pw)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
