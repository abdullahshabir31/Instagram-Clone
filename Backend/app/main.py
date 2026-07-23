from fastapi import FastAPI

from app.config import settings
from app.routers import (
    users,
    auth,
    posts,
    likes,
    comments,
    follows,
    saved_posts,
    stories,
    reels,
    chat,
    notifications,
    explore,
    block
)


app = FastAPI(
    title="Pixora API",
    version="1.0.0",
    description="Backend API for Pixora Social Platform"
)


# Using Alembic for database migrations
# Base.metadata.create_all(bind=engine)


# Routers
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(likes.router)
app.include_router(comments.router)
app.include_router(follows.router)
app.include_router(saved_posts.router)
app.include_router(stories.router)
app.include_router(reels.router)
app.include_router(chat.router)
app.include_router(notifications.router)
app.include_router(explore.router)
app.include_router(block.router)


@app.get("/")
def root():

    return {
        "message": "Welcome to Pixora API 🚀",
        "database": settings.database_name
    }