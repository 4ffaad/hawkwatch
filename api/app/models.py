import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class VideoStatus(enum.StrEnum):
    pending = "pending"  # signed URL issued, upload not verified
    uploaded = "uploaded"  # object verified in storage


class JobStatus(enum.StrEnum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class IncidentCategory(enum.StrEnum):
    possible_fight = "possible_fight"
    fire_smoke = "fire_smoke"
    possible_fall = "possible_fall"


class ReviewDecision(enum.StrEnum):
    confirmed = "confirmed"
    dismissed = "dismissed"


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column(String(128), index=True)
    filename: Mapped[str] = mapped_column(String(512))
    content_type: Mapped[str] = mapped_column(String(128))
    declared_size: Mapped[int] = mapped_column(BigInteger)
    object_key: Mapped[str] = mapped_column(String(1024), unique=True)
    object_etag: Mapped[str | None] = mapped_column(String(256))
    status: Mapped[VideoStatus] = mapped_column(Enum(VideoStatus, name="video_status"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=_uuid)
    video_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("videos.id", ondelete="CASCADE"))
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status"), default=JobStatus.queued, index=True
    )
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    lease_token: Mapped[uuid.UUID | None]
    lease_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    video: Mapped[Video] = relationship()
    incidents: Mapped[list["Incident"]] = relationship(back_populates="job")


class Incident(Base):
    __tablename__ = "incidents"
    # Idempotency: a retried job cannot create a second copy of the same interval.
    __table_args__ = (UniqueConstraint("job_id", "category", "start_ms"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=_uuid)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    category: Mapped[IncidentCategory] = mapped_column(Enum(IncidentCategory, name="incident_category"))
    start_ms: Mapped[int] = mapped_column(Integer)
    end_ms: Mapped[int] = mapped_column(Integer)
    score: Mapped[float] = mapped_column(Float)
    model_version: Mapped[str] = mapped_column(String(128))
    evidence_key: Mapped[str | None] = mapped_column(String(1024))
    summary: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    job: Mapped[Job] = relationship(back_populates="incidents")
    reviews: Mapped[list["Review"]] = relationship(back_populates="incident")


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=_uuid)
    incident_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("incidents.id", ondelete="CASCADE"), index=True
    )
    reviewer_id: Mapped[str] = mapped_column(String(128))
    decision: Mapped[ReviewDecision] = mapped_column(Enum(ReviewDecision, name="review_decision"))
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    incident: Mapped[Incident] = relationship(back_populates="reviews")
