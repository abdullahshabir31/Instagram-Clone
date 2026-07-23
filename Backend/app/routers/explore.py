from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app import models


router = APIRouter(
    prefix="/explore",
    tags=["Explore"]
)


# Search Users
@router.get("/users")
def search_users(
    q: str,
    db: Session = Depends(get_db)
):

    users = db.query(models.User).filter(
        or_(
            models.User.username.ilike(f"%{q}%"),
            models.User.email.ilike(f"%{q}%")
        )
    ).all()


    return users



# Search Posts
@router.get("/posts")
def search_posts(
    q: str,
    db: Session = Depends(get_db)
):

    posts = db.query(models.Post).filter(
        models.Post.caption.ilike(f"%{q}%")
    ).all()


    return posts



# Explore Feed
@router.get("/")
def explore_posts(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):

    posts = db.query(models.Post).order_by(
        models.Post.created_at.desc()
    ).offset(skip).limit(limit).all()


    return posts