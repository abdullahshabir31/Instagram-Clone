from fastapi import FastAPI
from app.config import settings

app = FastAPI()


@app.get("/")
def root():
    return {
        "message": "Welcome to Instagram Clone API 🚀",
        "database": settings.database_name
    }