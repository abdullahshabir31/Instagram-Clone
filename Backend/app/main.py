from fastapi import FastAPI
from app.config import settings
from app.database import engine, Base
from app import models
from app.routers import users
from app.routers import auth
from app.routers import posts
from app.routers import likes
from app.routers import comments
from app.routers import follows
from app.routers import saved_posts

app = FastAPI()

Base.metadata.create_all(bind=engine)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(likes.router)
app.include_router(comments.router)
app.include_router(follows.router)
app.include_router(saved_posts.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Instagram Clone API 🚀",
        "database": settings.database_name
    }