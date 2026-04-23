import os
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Secure Auth API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

password_hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-before-any-real-deployment")
ALGORITHM = "HS256"
TOKEN_EXPIRY_MINUTES = 30
MAX_FAILED_ATTEMPTS = 5

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

users_db: dict = {}
failed_attempts: dict = {}


class UserIn(BaseModel):
    username: str
    password: str

    @field_validator("username", "password")
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("field cannot be empty")
        return v


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return password_hasher.verify(plain, hashed)


def create_token(username: str) -> str:
    expiry = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRY_MINUTES)
    return jwt.encode({"sub": username, "exp": expiry}, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username or username not in users_db:
            raise credentials_error
    except JWTError:
        raise credentials_error
    return username


@app.get("/")
def root():
    return {"status": "running", "version": "1.0.0"}


@app.post("/register")
def register(user: UserIn):
    if user.username in users_db:
        return {"error": "Username already taken"}
    users_db[user.username] = hash_password(user.password)
    return {"message": f"Account created for '{user.username}'"}


@app.post("/login")
@limiter.limit("5/minute")
def login(request: Request, user: UserIn):
    if failed_attempts.get(user.username, 0) >= MAX_FAILED_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account locked — too many failed attempts.",
        )
    if user.username not in users_db:
        return {"error": "User not found"}

    if not verify_password(user.password, users_db[user.username]):
        failed_attempts[user.username] = failed_attempts.get(user.username, 0) + 1
        remaining = MAX_FAILED_ATTEMPTS - failed_attempts[user.username]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Wrong password. {remaining} attempt{'s' if remaining != 1 else ''} remaining.",
        )

    failed_attempts[user.username] = 0
    return {
        "access_token": create_token(user.username),
        "token_type": "bearer",
    }


@app.get("/dashboard")
def dashboard(current_user: str = Depends(get_current_user)):
    return {
        "message": f"Authenticated as {current_user}.",
        "data": "Protected endpoint — JWT verified.",
    }