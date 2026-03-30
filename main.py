from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Rate limiter - tracks requests/attempts by IP address
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Secure Auth API",
    description="A secure authentication API built with FastAPI, JWT and bcrypt",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS allows frontend which is our web page to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Using bcrypt for secure password hashing
password_hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = "supersecretkey123formygithubviewers" # WARNING: Move this to an environment variable before any real deployment
ALGORITHM = "HS256"
TOKEN_EXPIRY_BY_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# In-memory user store - will be replaced with a real database later
users_db = {}

# This is to track failed login attempts per username
login_attempts = {}
MAX_FAILED_ATTEMPTS = 5


class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str


def hash_password(password: str):
    return password_hasher.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return password_hasher.verify(plain_password, hashed_password)

def generate_token(data: dict):
    token_data = data.copy()
    expiry = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRY_BY_MINUTES)
    token_data.update({"exp": expiry})
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return token

def get_current_user(token: str = Depends(oauth2_scheme)):
    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise auth_error
    except JWTError:
        raise auth_error

    if username not in users_db:
        raise auth_error

    return username


@app.get("/")
def read_root():
    return {
        "message": "Secure Auth API by Shrish",
        "version": "1.0",
        "status": "running"
    }

@app.post("/register")
def register(user: UserRegister):
    if user.username in users_db:
        return {"error": "Username already taken"}

    users_db[user.username] = {
        "username": user.username,
        "hashed_password": hash_password(user.password)
    }

    return {"message": f"Account created for '{user.username}'!"}

@app.post("/login")
@limiter.limit("5/minute")
def login(request: Request, user: UserLogin):
    # This will block if too many failed attempts
    if login_attempts.get(user.username, 0) >= MAX_FAILED_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account locked due to too many failed attempts. Try again later."
        )

    if user.username not in users_db:
        return {"error": "User not found"}

    user_record = users_db[user.username]

    if not verify_password(user.password, user_record["hashed_password"]):
        # Increment failed attempts
        login_attempts[user.username] = login_attempts.get(user.username, 0) + 1
        attempts_left = MAX_FAILED_ATTEMPTS - login_attempts[user.username]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Wrong password. {attempts_left} attempts remaining."
        )

    # Resets the failed attempts on successful login
    login_attempts[user.username] = 0

    access_token = generate_token(data={"sub": user.username})
    return {
        "message": f"Welcome back, {user.username}!",
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/dashboard")
def dashboard(current_user: str = Depends(get_current_user)):
    return {
        "message": f"Hey {current_user}, welcome to your dashboard!",
        "data": "You are accessing protected data successfully."
    }