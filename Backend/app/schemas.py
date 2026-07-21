from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str | None = None
    bio: str | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str | None
    bio: str | None
    profile_image: str | None
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PostCreate(BaseModel):
    caption: str | None = None
    image_url: str


class PostResponse(BaseModel):
    id: int
    caption: str | None
    image_url: str
    created_at: datetime

    owner: UserMiniResponse

    likes_count: int
    comments_count: int

    model_config = {
        "from_attributes": True
    }

class FeedResponse(BaseModel):
    id: int
    caption: str | None
    image_url: str
    created_at: datetime

    owner: UserMiniResponse

    likes_count: int
    comments_count: int

    model_config = {
        "from_attributes": True
    }

class LikeResponse(BaseModel):
    id: int
    user_id: int
    post_id: int

    class Config:
        from_attributes = True

class CommentCreate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: int
    content: str
    user_id: int
    post_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class FollowResponse(BaseModel):
    id: int
    follower_id: int
    following_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ProfileResponse(BaseModel):
    id: int
    username: str
    email: str
    posts_count: int
    followers_count: int
    following_count: int

    class Config:
        from_attributes = True

class UserMiniResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class UserSearchResponse(BaseModel):
    id: int
    username: str
    full_name: str | None
    profile_image: str | None

    model_config = {
        "from_attributes": True
    }

class UserUpdate(BaseModel):
    username: str | None = None
    full_name: str | None = None
    bio: str | None = None

class ChangePassword(BaseModel):
    current_password: str
    new_password: str

class SavedPostResponse(BaseModel):
    id: int
    user_id: int
    post_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class SavedPostItem(BaseModel):
    id: int
    caption: str | None
    image_url: str
    owner_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }