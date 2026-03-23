# Secure Authentication API 🔐

A backend authentication system built with FastAPI, designed to demonstrate secure user authentication, JWT token management, and brute-force protection.

Built by Shrish Arunesh — CS student in Berlin passionate about cybersecurity and backend development. This project was built as a hands-on learning exercise to deeply understand authentication systems, security concepts and full stack development.

---

## 🛠️ Tech Stack

- **Python** — core language
- **FastAPI** — backend API framework
- **bcrypt** — secure password hashing
- **JWT (JSON Web Tokens)** — session authentication
- **SlowAPI** — rate limiting and brute-force defense
- **HTML, CSS, JavaScript** — frontend dashboard

---

## 🔍 Features

- User registration with secure bcrypt password hashing
- JWT token generation on login with 30 minute expiry
- Protected routes — accessible only with a valid token
- Rate limiting — max 5 login requests per minute per IP
- Brute force defense — account lockout after 5 failed attempts
- Interactive frontend dashboard with animated background
- Full error handling and user feedback

---

## 🚀 How to Run Locally

### 1 — Clone the repository
```bash [in your terminal]
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

## 🔐 Security Features

**Password Hashing** — Passwords are hashed using bcrypt before storage. The original password is never saved anywhere.

**JWT Authentication** — After login, a signed JWT token is issued with a 30 minute expiry. Protected routes verify this token on every request.

**Rate Limiting** — Login endpoint is limited to 5 requests per minute per IP address using SlowAPI.

**Brute Force Defense** — Accounts are locked after 5 consecutive failed login attempts.

---

## 📁 Project Structure
```
secure-auth-api/
│
├── main.py           # FastAPI backend — all endpoints and logic
├── README.md         # Project documentation
└── frontend/
    └── index.html    # Frontend dashboard
```

---

## 👨‍💻 Author

Shrish Arunesh