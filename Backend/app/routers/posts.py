from fastapi import APIRouter, Depends, status, File, UploadFile
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from fastapi import HTTPException
from app.database import get_db
from app import models, schemas, oauth2, cloudinary

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(
    caption: str,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):

    image_url = cloudinary.upload_image(image.file)

    new_post = models.Post(
        caption=caption,
        image_url=image_url,
        owner_id=current_user.id
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    # Owner relationship load karne ke liye
    new_post = db.query(models.Post).options(
        joinedload(models.Post.owner)
    ).filter(
        models.Post.id == new_post.id
    ).first()

    return {
        "id": new_post.id,
        "caption": new_post.caption,
        "image_url": new_post.image_url,
        "created_at": new_post.created_at,
        "owner": new_post.owner,
        "likes_count": 0,
        "comments_count": 0
    }


@router.get("/", response_model=list[schemas.PostResponse])
def get_posts(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):

    posts = (
    db.query(models.Post)
    .options(joinedload(models.Post.owner))
    .offset(skip)
    .limit(limit)
    .all()
)


    response = []

    for post in posts:

        response.append({
            "id": post.id,
            "caption": post.caption,
            "image_url": post.image_url,
            "created_at": post.created_at,

            "owner": post.owner,

            "likes_count": len(post.likes),

            "comments_count": db.query(models.Comment).filter(
                models.Comment.post_id == post.id
            ).count()
        })


    return response

@router.get("/feed", response_model=list[schemas.FeedResponse])
def get_feed(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):

    following_users = db.query(models.Follow.following_id).filter(
        models.Follow.follower_id == current_user.id
    ).all()


    following_ids = [
        user[0] for user in following_users
    ]

    following_ids.append(current_user.id)


    posts = (
    db.query(models.Post)
    .options(joinedload(models.Post.owner))
    .filter(models.Post.owner_id.in_(following_ids))
    .order_by(models.Post.created_at.desc())
    .offset(skip)
    .limit(limit)
    .all()
)


    response = []

    for post in posts:
        response.append({
            "id": post.id,
            "caption": post.caption,
            "image_url": post.image_url,
            "created_at": post.created_at,
            "owner": post.owner,
            "likes_count": len(post.likes),
            "comments_count": db.query(models.Comment).filter(
                models.Comment.post_id == post.id
            ).count()
        })


    return response

@router.get("/{id}", response_model=schemas.PostResponse)
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    return post

@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(
    id: int,
    updated_post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this post"
        )

    post_query.update(updated_post.model_dump(), synchronize_session=False)

    db.commit()

    return post_query.first()

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this post"
        )

    post_query.delete(synchronize_session=False)

    db.commit()

