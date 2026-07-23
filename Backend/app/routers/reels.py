from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app import models, schemas, oauth2, cloudinary


router = APIRouter(
    prefix="/reels",
    tags=["Reels"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_reel(
    caption: str = Form(None),
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

    return new_reel



@router.get("/")
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



@router.get("/user/{user_id}")
def get_user_reels(
    user_id: int,
    db: Session = Depends(get_db)
):

    reels = db.query(models.Reel).filter(
        models.Reel.owner_id == user_id
    ).all()

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


    if not reel:
        raise HTTPException(
            status_code=404,
            detail="Reel not found"
        )


    if reel.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )


    db.delete(reel)
    db.commit()


    return {
        "message": "Reel deleted successfully"
    }