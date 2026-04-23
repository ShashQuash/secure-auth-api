# Secure Authentication API

Backend authentication system built with FastAPI, implementing JWT token management, bcrypt password hashing, rate limiting, and brute-force protection.

Built by Shrish Arunesh — CS student in Berlin, focused on cybersecurity and backend development.

---

## Live Demo

| | |
|---|---|
| Frontend | [shashquash.github.io/secure-auth-api/frontend](https://shashquash.github.io/secure-auth-api/frontend) |
| API Docs | [secure-auth-api-clla.onrender.com/docs](https://secure-auth-api-clla.onrender.com/docs) |

---

## Stack

Python · FastAPI · bcrypt · JWT · SlowAPI · HTML · CSS · JavaScript

---

## Security Implementation

**Password Hashing** — Passwords are hashed with bcrypt before storage. The original password is never saved.

**JWT Authentication** — A signed JWT token is issued on login with a 30-minute expiry. Protected routes verify the token on every request.

**Rate Limiting** — Login endpoint is capped at 5 requests per minute per IP using SlowAPI.

**Brute Force Defense** — Accounts are locked after 5 consecutive failed login attempts.

**Input Validation** — All fields validated server-side. Empty or malformed inputs are rejected before reaching business logic.

**Secret Key** — Loaded from environment variable. Never hardcoded in source.

---

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | Status check | No |
| POST | `/register` | Register a new user | No |
| POST | `/login` | Login and receive JWT token | No |
| GET | `/dashboard` | Protected endpoint | Yes |

---

## Running Locally

```bash
git clone https://github.com/ShashQuash/secure-auth-api.git
cd secure-auth-api
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

API at `http://127.0.0.1:8000` · Docs at `http://127.0.0.1:8000/docs`

Open `frontend/index.html` with Live Server in VS Code to use the frontend.

---

## Project Structure

```
secure-auth-api/
├── main.py
├── requirements.txt
├── README.md
└── frontend/
    └── index.html
```

---

## Author

Shrish Arunesh · [Portfolio](https://shashquash.github.io/portfolio) · [GitHub](https://github.com/ShashQuash)