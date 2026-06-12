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
    allow_origins=["*"],  # TODO: restrict to the known frontend origin in production
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

password_hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-before-any-real-deployment")
ALGORITHM = "HS256"
TOKEN_EXPIRY_MINUTES = 30
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15  # how long an account stays locked after too many failures

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# NOTE: in-memory stores. They reset on restart and are not shared across
# multiple worker processes. Fine for a demo; a real deployment would use a
# database + a shared cache (e.g. Redis) for users and lockout state.
users_db: dict = {}
# username -> {"count": int, "locked_until": datetime | None}
failed_attempts: dict = {}

# Pre-computed hash used to equalise response timing when a username does not
# exist. Without this, a missing user skips bcrypt (fast) while a real user
# runs it (slow), letting an attacker enumerate valid usernames by timing.
_DUMMY_HASH = password_hasher.hash("constant-time-placeholder")


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


def is_locked(username: str) -> bool:
    """Return True if the account is currently within an active lockout window.
    Expired lockouts are cleared here so the user can try again afterwards."""
    record = failed_attempts.get(username)
    if not record:
        return False
    locked_until = record.get("locked_until")
    if locked_until is None:
        return False
    if datetime.now(timezone.utc) < locked_until:
        return True
    # Lockout window has passed — reset so a correct password works again.
    failed_attempts.pop(username, None)
    return False


def register_failure(username: str) -> None:
    record = failed_attempts.get(username, {"count": 0, "locked_until": None})
    record["count"] += 1
    if record["count"] >= MAX_FAILED_ATTEMPTS:
        record["locked_until"] = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_MINUTES)
    failed_attempts[username] = record


def reset_failures(username: str) -> None:
    failed_attempts.pop(username, None)


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


@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserIn):
    if user.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )
    users_db[user.username] = hash_password(user.password)
    return {"message": f"Account created for '{user.username}'"}


@app.post("/login")
@limiter.limit("5/minute")
def login(request: Request, user: UserIn):
    # Single generic error for every failure path so the response never reveals
    # whether the username exists or the password was wrong (anti-enumeration).
    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
    )

    if is_locked(user.username):
        # NOTE: lockout is keyed on username, so a malicious caller can lock a
        # known victim for LOCKOUT_MINUTES (availability vs. credential-stuffing
        # trade-off). The per-IP SlowAPI limit above blunts a single attacker.
        # Production options: key on IP+username, exponential backoff, or CAPTCHA.
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Account temporarily locked due to repeated failed logins. Try again later.",
        )

    stored_hash = users_db.get(user.username)

    if stored_hash is None:
        # Burn the same time a real bcrypt check would, then fail generically.
        verify_password(user.password, _DUMMY_HASH)
        register_failure(user.username)
        raise invalid_credentials

    if not verify_password(user.password, stored_hash):
        register_failure(user.username)
        raise invalid_credentials

    reset_failures(user.username)
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