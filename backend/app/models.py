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

# New models for recording pipeline
class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    kind: Mapped[str] = mapped_column(String(64))  # e.g., 'analysis'
    status: Mapped[str] = mapped_column(String(32), default="pending")  # pending|running|done|error
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

class Recording(Base):
    __tablename__ = "recordings"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, default=1)
    file_path: Mapped[str] = mapped_column(String(512))
    mime_type: Mapped[str] = mapped_column(String(128), default="audio/webm")
    status: Mapped[str] = mapped_column(String(32), default="uploaded")  # uploaded|processing|done|error
    job_id: Mapped[int | None] = mapped_column(ForeignKey("jobs.id"), nullable=True)
    analysis_result: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

class SongDraft(Base):
    __tablename__ = "song_drafts"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recording_id: Mapped[int | None] = mapped_column(ForeignKey("recordings.id"), nullable=True)
    meta: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    bpm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sections: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    chords: Mapped[str | None] = mapped_column(Text, nullable=True)
    lyrics: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    status: Mapped[str] = mapped_column(String(32), default="draft_ready")  # pending|analyzing|draft_ready|error|promoted
    song_id: Mapped[int | None] = mapped_column(ForeignKey("songs.id"), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
