from fastapi import FastAPI
from app.config import settings
from app.database import engine, Base
from app import models

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "message": "Welcome to Instagram Clone API 🚀",
        "database": settings.database_name
    }