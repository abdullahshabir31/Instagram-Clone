from fastapi import APIRouter, Depends, status, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas, oauth2, utils, cloudinary


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    new_user = models.User(
        username=user.username,
        email=user.email,
        password=utils.hash(user.password),
        full_name=user.full_name,
        bio=user.bio
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.get("/me", response_model=schemas.ProfileResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):

    posts_count = db.query(models.Post).filter(
        models.Post.owner_id == current_user.id
    ).count()


    followers_count = db.query(models.Follow).filter(
        models.Follow.following_id == current_user.id
    ).count()


    following_count = db.query(models.Follow).filter(
        models.Follow.follower_id == current_user.id
    ).count()


    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "posts_count": posts_count,
        "followers_count": followers_count,
        "following_count": following_count
    }

@router.get("/profile/{user_id}", response_model=schemas.ProfileResponse)
def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()


    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )


    posts_count = db.query(models.Post).filter(
        models.Post.user_id == user_id
    ).count()


    followers_count = db.query(models.Follow).filter(
        models.Follow.following_id == user_id
    ).count()


    following_count = db.query(models.Follow).filter(
        models.Follow.follower_id == user_id
    ).count()


    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "posts_count": posts_count,
        "followers_count": followers_count,
        "following_count": following_count
    }

@router.get("/search", response_model=list[schemas.UserSearchResponse])
def search_users(
    username: str,
    db: Session = Depends(get_db)
):

    users = db.query(models.User).filter(
        models.User.username.ilike(f"%{username}%")
    ).all()


    return users

@router.put("/me", response_model=schemas.UserResponse)
def update_profile(
    username: str | None = Form(None),
    full_name: str | None = Form(None),
    bio: str | None = Form(None),
    profile_image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):

    # Username update
    if username:
        existing_user = db.query(models.User).filter(
            models.User.username == username,
            models.User.id != current_user.id
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username already taken"
            )

        current_user.username = username

    # Full Name
    if full_name is not None:
        current_user.full_name = full_name

    # Bio
    if bio is not None:
        current_user.bio = bio

    # Profile Image
    if profile_image:
        image_url = cloudinary.upload_image(profile_image.file)
        current_user.profile_image = image_url

    db.commit()
    db.refresh(current_user)

    return current_user

@router.put("/change-password")
def change_password(
    passwords: schemas.ChangePassword,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):

    # Verify current password
    if not utils.verify(passwords.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Hash new password
    current_user.password = utils.hash(passwords.new_password)

    db.commit()

    return {
        "message": "Password changed successfully"
    }