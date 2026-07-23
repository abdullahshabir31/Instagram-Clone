from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app import cloudinary, models, oauth2, schemas


router = APIRouter(
    prefix="/reels",
    tags=["Reels"]
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.ReelResponse
)
def create_reel(
    caption: str | None = Form(None),
    video: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    video_url = cloudinary.upload_video(video.file)

    new_reel = models.Reel(
        video_url=video_url,
        caption=caption,
        owner_id=current_user.id
    )

    db.add(new_reel)
    db.commit()
    db.refresh(new_reel)

    new_reel = (
        db.query(models.Reel)
        .options(joinedload(models.Reel.owner))
        .filter(models.Reel.id == new_reel.id)
        .first()
    )

    return new_reel


@router.get("/", response_model=list[schemas.ReelResponse])
def get_reels(
    db: Session = Depends(get_db)
):
    reels = (
        db.query(models.Reel)
        .options(joinedload(models.Reel.owner))
        .order_by(models.Reel.created_at.desc())
        .all()
    )

    return reels


@router.get("/user/{user_id}", response_model=list[schemas.ReelResponse])
def get_user_reels(
    user_id: int,
    db: Session = Depends(get_db)
):
    reels = (
        db.query(models.Reel)
        .options(joinedload(models.Reel.owner))
        .filter(models.Reel.owner_id == user_id)
        .order_by(models.Reel.created_at.desc())
        .all()
    )

    return reels


@router.delete("/{id}")
def delete_reel(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    reel = db.query(models.Reel).filter(
        models.Reel.id == id
    ).first()

    if reel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reel not found"
        )

    if reel.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )

    db.delete(reel)
    db.commit()

    return {
        "message": "Reel deleted successfully"
    }