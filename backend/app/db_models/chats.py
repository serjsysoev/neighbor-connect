from datetime import datetime
from typing import List

from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import functions as func
from app.core.db import DBBase


class User(DBBase):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    login: Mapped[str] = mapped_column()
    password_hashed: Mapped[str] = mapped_column()
    birthday: Mapped[datetime | None] = mapped_column()
    additional_info: Mapped[str | None] = mapped_column()
    address: Mapped[str] = mapped_column()


class Message(DBBase):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(nullable=False)
    image_id: Mapped[int | None] = mapped_column(ForeignKey("images.id"), default=None)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped[User] = relationship()
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"))


class Tag(DBBase):
    __tablename__ = "tags"
    name: Mapped[str] = mapped_column(primary_key=True, index=True)


_chats_to_tags_assoc_table = Table(
    "chats_tags",
    DBBase.metadata,
    Column("chat_id", ForeignKey("chats.id", ondelete="CASCADE")),
    Column("tag_name", ForeignKey("tags.name", ondelete="CASCADE")),
)

_chats_to_users_assoc_table = Table(
    "chats_users",
    DBBase.metadata,
    Column("chat_id", ForeignKey("chats.id", ondelete="CASCADE")),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE")),
)

_chats_to_admins_assoc_table = Table(
    "chats_admins",
    DBBase.metadata,
    Column("chat_id", ForeignKey("chats.id", ondelete="CASCADE")),
    Column("admin_id", ForeignKey("users.id", ondelete="CASCADE")),
)


class Chat(DBBase):
    __tablename__ = "chats"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[str | None] = mapped_column()
    tags: Mapped[List[Tag]] = relationship(
        secondary=_chats_to_tags_assoc_table, cascade="all, delete"
    )
    image_id: Mapped[int | None] = mapped_column(ForeignKey("images.id"), default=None)
    users: Mapped[List[User]] = relationship(
        secondary=_chats_to_users_assoc_table, cascade="all, delete"
    )
    admins: Mapped[List[User]] = relationship(
        secondary=_chats_to_admins_assoc_table, cascade="all, delete"
    )
    messages: Mapped[List[Message]] = relationship(
        order_by="desc(Message.created_at)", cascade="all, delete"
    )


class Image(DBBase):
    __tablename__ = "images"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
