# Secure Authentication API

A FastAPI backend that handles the boring-but-critical parts of auth properly: bcrypt password hashing, JWT sessions, rate limiting, and a lockout that doesn't accidentally brick your own account. Built with a focus on the failure cases most tutorials skip.

Built by Shrish Arunesh, a CS student in Berlin working in backend and security.

## Live Demo

Frontend: [shashquash.github.io/secure-auth-api/frontend](https://shashquash.github.io/secure-auth-api/frontend)
API docs: [secure-auth-api-clla.onrender.com/docs](https://secure-auth-api-clla.onrender.com/docs)

Heads up: the backend sleeps on a free tier, so the first request after a quiet spell can take around 50 seconds to wake up. Give it a second and retry.

## Stack

Python, FastAPI, bcrypt (via passlib), python-jose for JWT, SlowAPI for rate limiting, and a plain HTML/CSS/JS frontend.

## What it does

**Passwords** are hashed with bcrypt before anything touches storage. The plaintext never gets saved.

**Login** returns a signed JWT (HS256) that lasts 30 minutes. Protected routes check the signature and expiry on every request.

**Rate limiting** caps the login endpoint at 5 requests per minute per IP, so a single attacker can't just hammer it.

**Account lockout** kicks in after 5 failed logins, but only for 15 minutes, then it clears itself. This was a deliberate fix: a naive counter that locks forever means one typo-happy user (or an attacker who knows their username) can permanently lock an account. The lockout stores an expiry time instead of a flag, so that can't happen here.

**No username leaks.** Every failed login gives the same generic "invalid username or password," whether the account exists or not. Even a login for a user that doesn't exist runs a throwaway bcrypt check, so you can't figure out which usernames are real by timing how fast the server says no.

**Sensible status codes.** Errors come back as 401, 409, or 429 depending on what went wrong, not a 200 with an error buried in the body.

## Endpoints

| Method | Endpoint | What it does | Auth |
|--------|----------|--------------|------|
| GET | `/` | Health check | No |
| POST | `/register` | Create an account (201) | No |
| POST | `/login` | Log in, get a JWT (200) | No |
| GET | `/dashboard` | Example protected route | Yes |

Errors you'll see: `401` for bad credentials or a bad token, `409` if the username is taken, `429` if the account is locked or you've hit the rate limit, `422` for an empty or malformed body.

## What it doesn't do (yet)

I'd rather be upfront about the gaps than pretend they aren't there:

- Users and lockout state live in memory, so they reset on restart and won't work across multiple workers. A real version would use a database plus something like Redis.
- The lockout is keyed on username, which means someone could deliberately lock a known account for 15 minutes. It's the classic availability-vs-brute-force tradeoff. The per-IP rate limit softens it, but the proper fix is keying on IP plus username or using backoff.
- The frontend keeps the JWT in `localStorage`, which is readable by JavaScript and so exposed if there's an XSS hole. An HttpOnly cookie would be safer; localStorage is just simpler for a demo.
- No refresh tokens and no way to revoke a token early. Once issued, it's valid until it expires.

## Running it locally

```bash
git clone https://github.com/ShashQuash/secure-auth-api.git
cd secure-auth-api
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

API runs at `http://127.0.0.1:8000`, docs at `/docs`. Open `frontend/index.html` with Live Server to use the UI.

Set a real signing key before deploying anywhere:

```bash
$env:SECRET_KEY = "your-long-random-secret"   # PowerShell
export SECRET_KEY="your-long-random-secret"    # macOS / Linux
```

## Layout

```
secure-auth-api/
├── main.py            # the whole API: auth, lockout, JWT
├── requirements.txt
├── Procfile
├── README.md
└── frontend/
    └── index.html
```

## Author

Shrish Arunesh: [Portfolio](https://shashquash.github.io/portfolio) · [GitHub](https://github.com/ShashQuash)