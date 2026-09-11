# Secure Authentication API

A FastAPI backend that handles the boring-but-critical parts of auth properly: bcrypt password hashing, JWT sessions, rate limiting, and a lockout that doesn't accidentally brick your own account. Built with a focus on the failure cases most tutorials skip.

Built by Shrish Arunesh, a graduating CS student in Berlin working with backend and security concepts.

## Live Demo

Frontend: [shashquash.github.io/secure-auth-api/frontend](https://shashquash.github.io/secure-auth-api/frontend)
API docs: [secure-auth-api-clla.onrender.com/docs](https://secure-auth-api-clla.onrender.com/docs)

Heads up: the backend sleeps on a free tier, so the first request after a quiet spell can take around 50 seconds to wake up. Give it a second and retry.

## Stack

Python, FastAPI, bcrypt (via passlib), python-jose for JWT, SlowAPI for rate limiting, and a plain HTML/CSS/JS frontend.

## What it does

**Passwords** are hashed with bcrypt before anything touches storage. The plaintext never gets saved.

**Password length is bounded at both ends**, and the upper bound is the interesting one. bcrypt only reads the first 72 *bytes* of a password and silently ignores everything after that. Without a cap, a 100-character password looks accepted but is only partly verified, and any other password sharing those first 72 bytes would authenticate just as well. So registration rejects anything over 72 bytes, counting bytes rather than characters, because one euro sign is three bytes and a naive character count would let it through. Minimum is 8.

**Login** returns a signed JWT (HS256) that lasts 30 minutes. Protected routes check the signature and expiry on every request.

**Rate limiting** caps login at 5 requests per minute per IP and registration at 10. Registration needs it as much as login does: users live in an in-memory dictionary, so an unthrottled register endpoint is a way to grow that dictionary until the process runs out of memory.

**Account lockout** kicks in after 5 failed logins, but only for 15 minutes, then it clears itself. This was a deliberate fix: a naive counter that locks forever means one typo-happy user (or an attacker who knows their username) can permanently lock an account. The lockout stores an expiry time instead of a flag, so that can't happen here.

**No username leaks.** Every failed login gives the same generic "invalid username or password," whether the account exists or not. Even a login for a user that doesn't exist runs a throwaway bcrypt check, so you can't figure out which usernames are real by timing how fast the server says no.

**Sensible status codes.** Errors come back as 401, 409, or 429 depending on what went wrong, not a 200 with an error buried in the body.

## Endpoints

| Method | Endpoint | What it does | Auth | Rate limit |
|--------|----------|--------------|------|------------|
| GET | `/` | Health check | No | none |
| POST | `/register` | Create an account (201) | No | 10/min per IP |
| POST | `/login` | Log in, get a JWT (200) | No | 5/min per IP |
| GET | `/dashboard` | Example protected route | Yes | none |

Errors you'll see: `401` for bad credentials or a bad token, `409` if the username is taken, `429` if the account is locked or you've hit the rate limit, `422` for an empty or malformed body or a password outside the length bounds.

## What it doesn't do (yet)

I'd rather be upfront about the gaps than pretend they aren't there:

- Users and lockout state live in memory, so they reset on restart and won't work across multiple workers. A real version would use a database plus something like Redis.
- The lockout is keyed on username, which means someone could deliberately lock a known account for 15 minutes. It's the classic availability-vs-brute-force tradeoff. The per-IP rate limit softens it, but the proper fix is keying on IP plus username or using backoff.
- `failed_attempts` is keyed on whatever username the caller sends, including ones that don't exist, so a determined caller can grow that dictionary. The per-IP rate limit is the only thing bounding it.
- CORS is still `allow_origins=["*"]`. Low risk here because credentials aren't allowed and auth is a Bearer header rather than a cookie, but it should be pinned to the known frontend origin.
- The frontend keeps the JWT in `localStorage`, which is readable by JavaScript and so exposed if there's an XSS hole. An HttpOnly cookie would be safer; localStorage is just simpler for a demo.
- No refresh tokens and no way to revoke a token early. Once issued, it's valid until it expires.

### Dependency debt

Worth stating separately, because these are known and not yet dealt with:

- `python-jose` is effectively unmaintained and has a published algorithm confusion issue. Every `decode` call here passes `algorithms=[ALGORITHM]` explicitly, which is the correct mitigation for that specific attack, but the library still needs replacing with PyJWT.
- `passlib` is unmaintained too. `bcrypt` is pinned to `4.0.1` because passlib breaks against bcrypt 4.1 and later. That pin works, and it also means this is stuck on a 2022 bcrypt until passlib is dropped in favour of the `bcrypt` library directly.
- Nothing else in `requirements.txt` is version pinned, so builds aren't reproducible and what's deployed drifts from what was tested.

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

Shrish Arunesh
