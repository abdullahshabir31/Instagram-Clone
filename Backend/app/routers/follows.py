from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, oauth2


router = APIRouter(
    prefix="/users",
    tags=["Follows"]
)


@router.post("/{user_id}/follow", status_code=status.HTTP_201_CREATED)
def follow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # Self follow check
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot follow yourself"
        )

    # Check user exists
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if receiver blocked current user
    blocked = db.query(models.Block).filter(
        models.Block.blocker_id == user_id,
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
        models.Block.blocked_id == user_id
    ).first()

    if blocked_by_you:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You blocked this user"
        )

    # Already following check
    existing_follow = db.query(models.Follow).filter(
        models.Follow.follower_id == current_user.id,
        models.Follow.following_id == user_id
    ).first()

    if existing_follow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already following this user"
        )

    # Private account
    if user.is_private:
        existing_request = db.query(models.FollowRequest).filter(
            models.FollowRequest.sender_id == current_user.id,
            models.FollowRequest.receiver_id == user_id,
            models.FollowRequest.status == "pending"
        ).first()

        if existing_request:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Follow request already sent"
            )

        follow_request = models.FollowRequest(
            sender_id=current_user.id,
            receiver_id=user_id,
            status="pending"
        )

        notification = models.Notification(
            sender_id=current_user.id,
            receiver_id=user_id,
            type="follow_request",
            message=f"{current_user.username} sent you a follow request"
        )

        db.add(follow_request)
        db.add(notification)
        db.commit()

        return {
            "message": "Follow request sent"
        }

    # Public account
    new_follow = models.Follow(
        follower_id=current_user.id,
        following_id=user_id
    )

    notification = models.Notification(
        sender_id=current_user.id,
        receiver_id=user_id,
        type="follow",
        message=f"{current_user.username} started following you"
    )

    db.add(new_follow)
    db.add(notification)

    db.commit()
    db.refresh(new_follow)

    return new_follow

@router.get("/follow-requests")
def get_follow_requests(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    requests = db.query(models.FollowRequest).filter(
        models.FollowRequest.receiver_id == current_user.id,
        models.FollowRequest.status == "pending"
    ).all()

    return requests


@router.put("/follow-requests/{request_id}/accept")
def accept_follow_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    request = db.query(models.FollowRequest).filter(
        models.FollowRequest.id == request_id,
        models.FollowRequest.receiver_id == current_user.id
    ).first()

    if request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow request not found"
        )

    new_follow = models.Follow(
        follower_id=request.sender_id,
        following_id=current_user.id
    )

    request.status = "accepted"

    notification = models.Notification(
        sender_id=current_user.id,
        receiver_id=request.sender_id,
        type="follow",
        message=f"{current_user.username} accepted your follow request"
    )

    db.add(new_follow)
    db.add(notification)

    db.commit()

    return {
        "message": "Follow request accepted"
    }


@router.put("/follow-requests/{request_id}/reject")
def reject_follow_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    request = db.query(models.FollowRequest).filter(
        models.FollowRequest.id == request_id,
        models.FollowRequest.receiver_id == current_user.id
    ).first()

    if request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow request not found"
        )

    request.status = "rejected"

    db.commit()

    return {
        "message": "Follow request rejected"
    }


@router.delete("/{user_id}/follow")
def unfollow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    follow = db.query(models.Follow).filter(
        models.Follow.follower_id == current_user.id,
        models.Follow.following_id == user_id
    ).first()

    if follow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow not found"
        )

    db.delete(follow)
    db.commit()

    return {
        "message": "Unfollowed successfully"
    }


@router.get("/{user_id}/followers")
def get_followers(
    user_id: int,
    db: Session = Depends(get_db)
):
    followers = db.query(models.Follow).filter(
        models.Follow.following_id == user_id
    ).all()

    return {
        "total_followers": len(followers),
        "followers": followers
    }


@router.get("/{user_id}/following")
def get_following(
    user_id: int,
    db: Session = Depends(get_db)
):
    following = db.query(models.Follow).filter(
        models.Follow.follower_id == user_id
    ).all()

    return {
        "total_following": len(following),
        "following": following
    }