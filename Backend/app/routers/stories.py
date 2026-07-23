from fastapi import APIRouter, Depends, UploadFile, File, status, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.database import get_db
from app import models, schemas, oauth2, cloudinary


router = APIRouter(
    prefix="/stories",
    tags=["Stories"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.StoryResponse)
def create_story(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):

    image_url = cloudinary.upload_image(image.file)


    new_story = models.Story(
        media_url=image_url,
        owner_id=current_user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
    )


    db.add(new_story)
    db.commit()
    db.refresh(new_story)


    return new_story

@router.get("/", response_model=list[schemas.StoryResponse])
def get_stories(
    db: Session = Depends(get_db)
):

    stories = db.query(models.Story).filter(
        models.Story.expires_at > datetime.now(timezone.utc)
    ).all()


    return stories

@router.get("/user/{user_id}", response_model=list[schemas.StoryResponse])
def get_user_stories(
    user_id: int,
    db: Session = Depends(get_db)
):

    stories = db.query(models.Story).filter(
        models.Story.owner_id == user_id,
        models.Story.expires_at > datetime.now(timezone.utc)
    ).all()


    return stories

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_story(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):

    story_query = db.query(models.Story).filter(
        models.Story.id == id
    )

    story = story_query.first()


    if story is None:
        raise HTTPException(
            status_code=404,
            detail="Story not found"
        )


    if story.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )


    story_query.delete(
        synchronize_session=False
    )

    db.commit()