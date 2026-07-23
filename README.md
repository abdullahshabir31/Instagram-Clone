# 🚀 Pixora

**Pixora** is a modern full-stack social media platform inspired by today's leading social networking applications. It is built with **React.js**, **FastAPI**, and **PostgreSQL**, following a scalable and production-ready architecture.

---

## 🚀 Tech Stack

### Frontend

- React.js
- Vite
- JavaScript
- React Router DOM
- Axios
- Tailwind CSS

### Backend

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- JWT Authentication
- Pydantic

---

## ✨ Current Features

### 🔐 Authentication

- User Registration
- User Login
- JWT Authentication
- Secure Password Hashing
- Protected Routes

### 👤 User Profiles

- View Profile
- Edit Profile
- Profile Picture
- Bio
- Follow / Unfollow Users
- Followers & Following

### 📸 Posts

- Create Posts
- Upload Images
- Captions
- Edit Posts
- Delete Posts

### ❤️ Social Features

- Like / Unlike Posts
- Comment System
- Save Posts
- User Search
- Home Feed

---

## 🚀 Upcoming Features

- Stories
- Shorts (Vertical Videos)
- Real-Time Chat
- Notifications
- Explore Page
- Search
- AI Caption Generator
- AI Hashtag Generator

---

## 📂 Project Structure

```text
Pixora-Project/
│
├── Frontend/
│   ├── React Application
│   └── User Interface
│
├── Backend/
│   ├── FastAPI Application
│   ├── REST APIs
│   └── PostgreSQL Database
│
└── README.md
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone <repository-url>
```

Move into project folder

```bash
cd Pixora-Project
```

---

## Frontend

```bash
cd Frontend
npm install
npm run dev
```

---

## Backend

```bash
cd Backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

python -m uvicorn app.main:app --reload
```

API Documentation

```text
http://127.0.0.1:8000/docs
```

---

## 🗄️ Database

Pixora uses **PostgreSQL** with **SQLAlchemy ORM** and **Alembic** for database migrations.

---

## 🔗 Architecture

```text
React Frontend
        │
        │ Axios / REST API
        ▼
FastAPI Backend
        │
        ▼
PostgreSQL Database
```

---

## 📌 Status

🚧 Pixora is currently under active development.

New features and improvements are continuously being added.

---

## 👨‍💻 Author

**Abdullah Shabir**

## 🔗 Connect With Me

- GitHub: https://github.com/abdullahshabir31
- LinkedIn: https://www.linkedin.com/in/abdullahshabir31
- Portfolio: https://abdullah-shabir-portfolio.vercel.app/
