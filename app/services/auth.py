from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.repositories import user_repo
from app.db.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.jwt_secret, 
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def decode_access_token(token: str):
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = user_repo.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    return user

def hash_password(password: str) -> str:
    # lazy import to avoid circular dependency with security module
    from app.services.security import hash_password as _hash
    return _hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # lazy import to avoid circular dependency with security module
    from app.services.security import verify_password as _verify
    return _verify(plain_password, hashed_password)

# For testing convenience
def get_test_user(db: Session, user_id: int):
    return user_repo.get_user_by_id(db, user_id)