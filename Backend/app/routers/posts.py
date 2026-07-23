from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session, joinedload

from app import cloudinary, models, oauth2, schemas
from app.database import get_db


router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.PostResponse
)
def create_post(
    caption: str,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):

    image_url = cloudinary.upload_image(image.file)

    if not image_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Image upload failed"
        )

    new_post = models.Post(
        caption=caption,
        image_url=image_url,
        owner_id=current_user.id
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    new_post = (
        db.query(models.Post)
        .options(joinedload(models.Post.owner))
        .filter(models.Post.id == new_post.id)
        .first()
    )

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
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):

    blocked_users = db.query(models.Block.blocked_id).filter(
        models.Block.blocker_id == current_user.id
    ).all()

    blocked_by_users = db.query(models.Block.blocker_id).filter(
        models.Block.blocked_id == current_user.id
    ).all()

    blocked_ids = (
        [user[0] for user in blocked_users] +
        [user[0] for user in blocked_by_users]
    )

    posts = (
        db.query(models.Post)
        .options(joinedload(models.Post.owner))
        .filter(~models.Post.owner_id.in_(blocked_ids))
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

    following_ids = [user[0] for user in following_users]
    following_ids.append(current_user.id)

    blocked_users = db.query(models.Block.blocked_id).filter(
        models.Block.blocker_id == current_user.id
    ).all()

    blocked_by_users = db.query(models.Block.blocker_id).filter(
        models.Block.blocked_id == current_user.id
    ).all()

    blocked_ids = (
        [user[0] for user in blocked_users] +
        [user[0] for user in blocked_by_users]
    )

    posts = (
        db.query(models.Post)
        .options(joinedload(models.Post.owner))
        .filter(
            models.Post.owner_id.in_(following_ids),
            ~models.Post.owner_id.in_(blocked_ids)
        )
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
def get_post(
    id: int,
    db: Session = Depends(get_db)
):

    post = (
        db.query(models.Post)
        .options(joinedload(models.Post.owner))
        .filter(models.Post.id == id)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    return {
        "id": post.id,
        "caption": post.caption,
        "image_url": post.image_url,
        "created_at": post.created_at,
        "owner": post.owner,
        "likes_count": len(post.likes),
        "comments_count": db.query(models.Comment).filter(
            models.Comment.post_id == post.id
        ).count()
    }


@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(
    id: int,
    updated_post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):

    post_query = db.query(models.Post).filter(
        models.Post.id == id
    )

    post = post_query.first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this post"
        )

    post_query.update(
        updated_post.model_dump(),
        synchronize_session=False
    )

    db.commit()

    updated = (
        db.query(models.Post)
        .options(joinedload(models.Post.owner))
        .filter(models.Post.id == id)
        .first()
    )

    return {
        "id": updated.id,
        "caption": updated.caption,
        "image_url": updated.image_url,
        "created_at": updated.created_at,
        "owner": updated.owner,
        "likes_count": len(updated.likes),
        "comments_count": db.query(models.Comment).filter(
            models.Comment.post_id == updated.id
        ).count()
    }


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):

    post_query = db.query(models.Post).filter(
        models.Post.id == id
    )

    post = post_query.first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this post"
        )

    post_query.delete(synchronize_session=False)
    db.commit()

    return