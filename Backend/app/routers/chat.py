from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app import cloudinary, models, oauth2, schemas


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("/send", response_model=schemas.MessageResponse)
def send_message(
    message: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # Check receiver exists
    receiver = db.query(models.User).filter(
        models.User.id == message.receiver_id
    ).first()

    if receiver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receiver not found"
        )

    # Check if receiver blocked current user
    blocked = db.query(models.Block).filter(
        models.Block.blocker_id == message.receiver_id,
        models.Block.blocked_id == current_user.id
    ).first()

    if blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are blocked by this user"
        )

    # Check if current user blocked receiver
    blocked_by_you = db.query(models.Block).filter(
        models.Block.blocker_id == current_user.id,
        models.Block.blocked_id == message.receiver_id
    ).first()

    if blocked_by_you:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You blocked this user"
        )

    # Create message
    new_message = models.Message(
        sender_id=current_user.id,
        receiver_id=message.receiver_id,
        message_type=message.message_type,
        content=message.content,
        file_url=message.file_url,
        file_name=message.file_name,
        file_size=message.file_size
    )

    # Create notification
    notification = models.Notification(
        sender_id=current_user.id,
        receiver_id=message.receiver_id,
        type="message",
        message=f"{current_user.username} sent you a message"
    )

    db.add(new_message)
    db.add(notification)

    db.commit()
    db.refresh(new_message)

    return new_message


@router.get("/{user_id}", response_model=list[schemas.MessageResponse])
def get_conversation(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    messages = db.query(models.Message).filter(
        or_(
            and_(
                models.Message.sender_id == current_user.id,
                models.Message.receiver_id == user_id
            ),
            and_(
                models.Message.sender_id == user_id,
                models.Message.receiver_id == current_user.id
            )
        )
    ).order_by(
        models.Message.created_at
    ).all()

    # Mark received messages as seen
    for message in messages:
        if message.receiver_id == current_user.id:
            message.is_seen = True

    db.commit()

    return messages

@router.post("/send-file", response_model=schemas.MessageResponse)
def send_file_message(
    receiver_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # Check receiver exists
    receiver = db.query(models.User).filter(
        models.User.id == receiver_id
    ).first()

    if receiver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receiver not found"
        )

    # Check if receiver blocked current user
    blocked = db.query(models.Block).filter(
        models.Block.blocker_id == receiver_id,
        models.Block.blocked_id == current_user.id
    ).first()

    if blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are blocked by this user"
        )

    # Check if current user blocked receiver
    blocked_by_you = db.query(models.Block).filter(
        models.Block.blocker_id == current_user.id,
        models.Block.blocked_id == receiver_id
    ).first()

    if blocked_by_you:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You blocked this user"
        )

    # Upload file
    upload_result = cloudinary.upload_file(file.file)

    # Detect message type
    if file.content_type.startswith("image"):
        message_type = "image"
    elif file.content_type.startswith("video"):
        message_type = "video"
    else:
        message_type = "document"

    # Create message
    new_message = models.Message(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        message_type=message_type,
        file_url=upload_result["url"],
        file_type=file.content_type,
        file_name=upload_result["name"],
        file_size=upload_result["size"]
    )

    # Create notification
    notification = models.Notification(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        type="message",
        message=f"{current_user.username} sent you a file"
    )

    db.add(new_message)
    db.add(notification)

    db.commit()
    db.refresh(new_message)

    return new_message


@router.get("/unread/count")
def unread_messages_count(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    count = db.query(models.Message).filter(
        models.Message.receiver_id == current_user.id,
        models.Message.is_seen.is_(False)
    ).count()

    return {
        "unread_messages": count
    }


@router.delete("/message/{message_id}")
def unsend_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    message = db.query(models.Message).filter(
        models.Message.id == message_id
    ).first()

    if message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    if message.sender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only unsend your own messages"
        )

    message.is_deleted = True
    message.content = "This message was unsent"
    message.file_url = None

    db.commit()

    return {
        "message": "Message unsent successfully"
    }