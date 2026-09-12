from __future__ import annotations
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from config import settings

'''User model that will all attributes related to user entity'''
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    image_file: Mapped[str | None] = mapped_column(String(200), nullable=True, default=None)

    posts: Mapped[list[Post]] = relationship(back_populates="author", cascade="all, delete-orphan") # What it tells Python/VS Code: "When I access user.posts, give me a Python list containing Post objects."

    reset_tokens: Mapped[list[PasswordResetToken]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"https://{settings.s3_bucket_name}.s3.{settings.s3_region}.amazonaws.com/profile_pics/{self.image_file}"
        return f"/static/profile_pics/default.jpg"
    
'''Post model that will have all attributes that any Post entity will have'''
class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    date_posted: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    likes : Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    author: Mapped[User] = relationship(back_populates="posts")

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    user: Mapped[User] = relationship(back_populates="reset_tokens")

# Parth's understanding 
'''
We are using SQLAlchemy ORM here so we can interact with SQL DB with python object syntax instead of SQL Queries.

User model - 
A user will have a name, an email ID, a password, a profile image, a list of posts that he/she will author, [many meta things like likes, comments, history etc in proper system]
Here, Mapped[int] is for python to understand what data type this field is and mapped_column is for DB to construct columns

We map a many to one elationship from Post model to User as one User may have many posts. when we back_populate posts to author, we mean each post will be related to User by author and 
the author field on post model will be back populated to posts

A post will also have its Title, content, user_id which will act as foreign key to User model (id), when the post was posted, author of post

'''