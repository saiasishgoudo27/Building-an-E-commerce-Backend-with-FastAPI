from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends, Security
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session
from Connection import get_db
from Models import User

SECRET_KEY = "suhwdqihwdknlkdiwadlskmdlkdj276y28y2isjjk"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password Hashing
pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

# OAuth2 scheme for token extraction from requests
oauth2scheme = OAuth2PasswordBearer(tokenUrl='token')
bearer_scheme = HTTPBearer()

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserAuth(BaseModel):
    username: str
    password: str
    email: str
    address: str
    phone: str
    role: str

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2scheme), db: Session = Depends(get_db)):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user_record = db.query(User).filter(User.username == token_data.username).first()
    if user_record is None:
        raise credentials_exception
    return user_record

async def get_current_active_user(current_user = Depends(get_current_user)):
    if hasattr(current_user, "disabled") and current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_user_from_bearer(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme), db: Session = Depends(get_db)):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user_record = db.query(User).filter(User.username == token_data.username).first()
    if user_record is None:
        raise credentials_exception
    return user_record

async def get_current_active_user_from_bearer(current_user = Depends(get_current_user_from_bearer)):
    if hasattr(current_user, "disabled") and current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
