from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, oauth2


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


@router.get("/", response_model=list[schemas.NotificationResponse])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    notifications = db.query(models.Notification).filter(
        models.Notification.receiver_id == current_user.id
    ).order_by(
        models.Notification.created_at.desc()
    ).all()

    return notifications


@router.get("/unread/count")
def unread_notifications_count(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    count = db.query(models.Notification).filter(
        models.Notification.receiver_id == current_user.id,
        models.Notification.is_read.is_(False)
    ).count()

    return {
        "unread_notifications": count
    }


@router.put("/read/{notification_id}")
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.receiver_id == current_user.id
    ).first()

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    notification.is_read = True

    db.commit()

    return {
        "message": "Notification marked as read"
    }


@router.put("/read-all")
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    db.query(models.Notification).filter(
        models.Notification.receiver_id == current_user.id,
        models.Notification.is_read.is_(False)
    ).update(
        {
            "is_read": True
        },
        synchronize_session=False
    )

    db.commit()

    return {
        "message": "All notifications marked as read"
    }