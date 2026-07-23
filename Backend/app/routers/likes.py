from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, oauth2


router = APIRouter(
    prefix="/posts",
    tags=["Likes"]
)


@router.post("/{post_id}/like", status_code=status.HTTP_201_CREATED)
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # Check if post exists
    post = db.query(models.Post).filter(
        models.Post.id == post_id
    ).first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # Check if post owner blocked current user
    if db.query(models.Block).filter(
        models.Block.blocker_id == post.owner_id,
        models.Block.blocked_id == current_user.id
    ).first():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are blocked by this user"
        )

    # Check if current user blocked post owner
    if db.query(models.Block).filter(
        models.Block.blocker_id == current_user.id,
        models.Block.blocked_id == post.owner_id
    ).first():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You blocked this user"
        )

    # Check if already liked
    existing_like = db.query(models.Like).filter(
        models.Like.post_id == post_id,
        models.Like.user_id == current_user.id
    ).first()

    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post already liked"
        )

    new_like = models.Like(
        post_id=post_id,
        user_id=current_user.id
    )

    db.add(new_like)

    # Create notification
    if post.owner_id != current_user.id:
        db.add(
            models.Notification(
                sender_id=current_user.id,
                receiver_id=post.owner_id,
                type="like",
                post_id=post.id,
                message=f"{current_user.username} liked your post"
            )
        )

    db.commit()
    db.refresh(new_like)

    return new_like


@router.delete("/{post_id}/like")
def unlike_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    like = db.query(models.Like).filter(
        models.Like.post_id == post_id,
        models.Like.user_id == current_user.id
    ).first()

    if like is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Like not found"
        )

    db.delete(like)
    db.commit()

    return {
        "message": "Post unliked successfully"
    }


@router.get("/{post_id}/likes")
def get_post_likes(
    post_id: int,
    db: Session = Depends(get_db)
):
    likes = db.query(models.Like).filter(
        models.Like.post_id == post_id
    ).all()

    return {
        "total_likes": len(likes),
        "likes": likes
    }