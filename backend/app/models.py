from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, Integer, DateTime, func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

class Song(Base):
    __tablename__ = "songs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(255), index=True)
    artist: Mapped[str] = mapped_column(String(255), default="")
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

class Section(Base):
    __tablename__ = "sections"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    song_id: Mapped[int] = mapped_column(ForeignKey("songs.id"))
    name: Mapped[str] = mapped_column(String(64))
    order_index: Mapped[int] = mapped_column(Integer)

class Line(Base):
    __tablename__ = "lines"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"))
    text: Mapped[str] = mapped_column(Text)
    chords_json: Mapped[str] = mapped_column(Text, default="[]")
    order_index: Mapped[int] = mapped_column(Integer)
