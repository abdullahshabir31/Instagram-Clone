from sqlalchemy import Column, Date, Integer, String, Boolean, TIMESTAMP, text, ForeignKey
from app.database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    profile_image = Column(String, nullable=True)
    is_active = Column(Boolean, server_default="TRUE", nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )
    posts = relationship("Post", back_populates="owner")
    stories = relationship(
    "Story",
    back_populates="owner",
    cascade="all, delete-orphan"
    )
    reels = relationship(
    "Reel",
    back_populates="owner",
    cascade="all, delete-orphan"
    )
    likes = relationship("Like", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    saved_posts = relationship("SavedPost", back_populates="user")
    website = Column(String, nullable=True)

    gender = Column(String, nullable=True)

    date_of_birth = Column(Date, nullable=True)

    is_private = Column(
    Boolean,
    server_default="FALSE",
    nullable=False
    )

    updated_at = Column(
    TIMESTAMP(timezone=True),
    server_default=text("CURRENT_TIMESTAMP"),
    onupdate=text("CURRENT_TIMESTAMP"),
    nullable=False
    )

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)
    caption = Column(String, nullable=True)
    image_url = Column(String, nullable=False)

    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )

    owner = relationship("User", back_populates="posts")

    likes = relationship(
    "Like",
    back_populates="post",
    cascade="all, delete-orphan"
    )

    comments = relationship(
    "Comment",
    back_populates="post",
    cascade="all, delete-orphan"
    )

    saved_posts = relationship(
    "SavedPost",
    back_populates="post",
    cascade="all, delete-orphan"
    )

class Story(Base):

    __tablename__ = "stories"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    media_url = Column(
        String,
        nullable=False
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )

    expires_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False
    )


    owner = relationship(
        "User",
        back_populates="stories"
    )

class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    post_id = Column(
        Integer,
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()")
    )


    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)

    content = Column(String, nullable=False)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    post_id = Column(
        Integer,
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()")
    )


    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)

    follower_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    following_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("now()")
    )

class SavedPost(Base):
    __tablename__ = "saved_posts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    post_id = Column(
        Integer,
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )

    user = relationship("User", back_populates="saved_posts")
    post = relationship("Post", back_populates="saved_posts")

class Reel(Base):
    __tablename__ = "reels"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    video_url = Column(
        String,
        nullable=False
    )

    caption = Column(
        String,
        nullable=True
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )

    owner = relationship(
        "User",
        back_populates="reels"
    )