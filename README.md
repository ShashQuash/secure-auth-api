# Secure Authentication API 🔐

A backend authentication system built with FastAPI, implementing secure user authentication, JWT token management, and brute-force protection.

Built by Shrish Arunesh — CS student in Berlin, focused on cybersecurity and backend development.

---

## 🌐 Live Demo

| | Link |
|---|---|
| **Frontend** | [Click to visit](https://shashquash.github.io/secure-auth-api/frontend) |
| **API Docs** | [Click to visit](https://secure-auth-api-clla.onrender.com/docs) |

---

## 🛠️ Tech Stack

- **Python** - core language
- **FastAPI** - backend API framework
- **bcrypt** - secure password hashing
- **JWT (JSON Web Tokens)** - session authentication
- **SlowAPI** - rate limiting and brute-force defense
- **HTML, CSS, JavaScript** - frontend dashboard

---

## 🔍 Features

- User registration with secure bcrypt password hashing
- JWT token generation on login with 30 minute expiry
- Protected routes — accessible only with a valid token
- Rate limiting — max 5 login requests per minute per IP
- Brute force defense — account lockout after 5 failed attempts
- Full error handling and user feedback

---

## 🔐 Security Implementation

**Password Hashing** — Passwords are hashed with bcrypt before storage. The original password is never saved.

**JWT Authentication** — A signed JWT token is issued on login with a 30-minute expiry. Protected routes verify the token on every request.

**Rate Limiting** — Login endpoint is capped at 5 requests per minute per IP using SlowAPI.

**Brute Force Defense** — Accounts are locked after 5 consecutive failed login attempts.

---

## 🚀 How to Run Locally

### 1 — Clone the repository
```bash
git clone https://github.com/ShashQuash/secure-auth-api.git
cd secure-auth-api
```

### 2 — Create and activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3 — Install dependencies
```bash
pip install fastapi uvicorn passlib bcrypt==4.0.1 python-jose slowapi
```

### 4 — Run the API
```bash
python -m uvicorn main:app --reload
```

### 5 — Open the frontend
Open `frontend/index.html` with Live Server in VS Code

---

## 📡 API Endpoints

| Method | Endpoint     | Description                 | Auth Required |
|--------|--------------|-----------------------------|---------------|
| GET    | `/`          | API status check            | No            |
| POST   | `/register`  | Register a new user         | No            |
| POST   | `/login`     | Login and receive JWT token | No            |
| GET    | `/dashboard` | Access protected dashboard  | Yes           |

---

## 📁 Project Structure

```
secure-auth-api/
│
├── main.py           # FastAPI backend — all endpoints and logic
├── README.md
└── frontend/
    └── index.html    # Frontend dashboard
```

---

## 👨‍💻 Author

Shrish Arunesh · [Portfolio](https://shashquash.github.io/portfolio) · [GitHub](https://github.com/ShashQuash)