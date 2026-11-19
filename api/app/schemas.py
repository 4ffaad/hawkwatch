import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import IncidentCategory, JobStatus, ReviewDecision


class UploadRequest(BaseModel):
    filename: str = Field(max_length=512)
    content_type: str = Field(pattern=r"^video/")
    size: int = Field(gt=0)


class UploadResponse(BaseModel):
    video_id: uuid.UUID
    upload_url: str


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    video_id: uuid.UUID
    status: JobStatus
    attempts: int
    error: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category: IncidentCategory
    start_ms: int
    end_ms: int
    score: float
    model_version: str
    summary: str | None
    latest_decision: ReviewDecision | None = None


class ReviewIn(BaseModel):
    decision: ReviewDecision
    note: str | None = Field(default=None, max_length=2000)
