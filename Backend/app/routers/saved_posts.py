from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app import models, schemas, oauth2


router = APIRouter(
    prefix="/users/me",
    tags=["Saved Posts"]
)


@router.get(
    "/saved-posts",
    response_model=list[schemas.SavedPostItem]
)
def get_saved_posts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):

    saved_posts = (
        db.query(models.SavedPost)
        .options(joinedload(models.SavedPost.post))
        .filter(models.SavedPost.user_id == current_user.id)
        .all()
    )

    return [saved.post for saved in saved_posts]


@router.post(
    "/saved-posts/{post_id}",
    response_model=schemas.SavedPostResponse,
    status_code=status.HTTP_201_CREATED
)
def save_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):

    # Check post exists
    post = db.query(models.Post).filter(
        models.Post.id == post_id
    ).first()

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    # Already saved?
    saved_post = db.query(models.SavedPost).filter(
        models.SavedPost.user_id == current_user.id,
        models.SavedPost.post_id == post_id
    ).first()

    if saved_post:
        raise HTTPException(
            status_code=400,
            detail="Post already saved"
        )

    new_saved_post = models.SavedPost(
        user_id=current_user.id,
        post_id=post_id
    )

    db.add(new_saved_post)
    db.commit()
    db.refresh(new_saved_post)

    return new_saved_post


@router.delete(
    "/saved-posts/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def unsave_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):

    saved_post = db.query(models.SavedPost).filter(
        models.SavedPost.user_id == current_user.id,
        models.SavedPost.post_id == post_id
    ).first()

    if not saved_post:
        raise HTTPException(
            status_code=404,
            detail="Saved post not found"
        )

    db.delete(saved_post)
    db.commit()

    return