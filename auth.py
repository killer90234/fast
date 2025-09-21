from datetime import datetime, timedelta, timezone 
from fastapi import HTTPException, Depends, status
from authlib.jose import jwt, JoseError
from passlib.context import CryptContext


SC = "secret_key" 
LOGIN_EXPIRE_MIN = 30
ALGO = "HS256"

pass_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash_password(normal_pass: str):
    return pass_context.hash(normal_pass)


def verify_password(normal_pass: str, hashed_pass: str):
    return pass_context.verify(normal_pass, hashed_pass)


def create_access_token(data: dict, expire_delta: timedelta = None):
    headers = {'alg': ALGO}
    expire = datetime.now(timezone.utc) + ( expire_delta or timedelta(LOGIN_EXPIRE_MIN))
    payload = data.copy()
    payload.update({'exp': expire})
    return jwt.encode(headers,payload, SC).decode('utf-8')


def decode_access_token(token: str):
    """Decode JWT token"""
    try:
        payload = jwt.decode(token, SC, algorithms=[ALGO])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")