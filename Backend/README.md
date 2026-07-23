# 🚀 Pixora - Backend

This is the backend of **Pixora**, a modern full-stack social media platform built with **FastAPI** and **PostgreSQL**.

The backend provides secure REST APIs for authentication, user management, posts, likes, comments, follows, saved posts, and other social media features. It follows a clean, scalable, and production-ready architecture using FastAPI, SQLAlchemy, and PostgreSQL.

---

## 🚀 Tech Stack

- Python
- FastAPI
- Uvicorn
- PostgreSQL
- SQLAlchemy
- Alembic
- JWT Authentication
- Passlib & Bcrypt
- Pydantic
- Python-dotenv

---

## 📂 Project Structure

```text
Backend/
│
├── app/
│   ├── main.py          # FastAPI application entry point
│   ├── database.py      # Database connection
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── oauth2.py        # JWT authentication
│   │
│   └── routers/         # API route modules
│
├── alembic/
├── requirements.txt
├── .env
└── venv/
```

---

## ⚙️ Installation & Setup

Clone the repository

```bash
git clone <repository-url>
```

Move into the backend folder

```bash
cd Backend
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the virtual environment

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file

```env
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
ALGORITHM=HS256
```

Run the development server

```bash
python -m uvicorn app.main:app --reload
```

API Documentation

```text
http://127.0.0.1:8000/docs
```

---

## ✨ Current Features

- User Registration
- User Login
- JWT Authentication
- Protected Routes
- User Profiles
- Create Posts
- Like Posts
- Comment System
- Follow / Unfollow Users
- Saved Posts

---

## 🗄️ Database

Pixora uses **PostgreSQL** as the primary database with **SQLAlchemy ORM** for database management.

---

## 📌 Status

🚧 Pixora Backend is currently under active development.

New APIs and features will be added continuously.

---

## 👨‍💻 Author

**Abdullah Shabir**

## 🔗 Connect With Me

- GitHub: https://github.com/abdullahshabir31
- LinkedIn: https://www.linkedin.com/in/abdullahshabir31
- Portfolio: https://abdullah-shabir-portfolio.vercel.app/
