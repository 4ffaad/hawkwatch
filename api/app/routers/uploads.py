import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import storage
from app.auth import current_user
from app.config import get_settings
from app.db import get_db
from app.models import Job, Video, VideoStatus
from app.schemas import JobOut, UploadRequest, UploadResponse

router = APIRouter(prefix="/uploads", tags=["uploads"])

Db = Annotated[Session, Depends(get_db)]
User = Annotated[str, Depends(current_user)]


@router.post("", response_model=UploadResponse, status_code=201)
def create_upload(body: UploadRequest, db: Db, user: User):
    if body.size > get_settings().max_upload_bytes:
        raise HTTPException(413, "File too large")
    video_id = uuid.uuid4()
    key = f"uploads/{user}/{video_id}"
    db.add(
        Video(
            id=video_id,
            owner_id=user,
            filename=body.filename,
            content_type=body.content_type,
            declared_size=body.size,
            object_key=key,
            status=VideoStatus.pending,
        )
    )
    db.commit()
    return UploadResponse(video_id=video_id, upload_url=storage.presign_put(key, body.content_type))


@router.post("/{video_id}/complete", response_model=JobOut, status_code=201)
def complete_upload(video_id: uuid.UUID, db: Db, user: User):
    video = db.get(Video, video_id, with_for_update=True)
    if video is None or video.owner_id != user:
        raise HTTPException(404, "Upload not found")
    if video.status != VideoStatus.pending:
        raise HTTPException(409, "Upload already completed")

    obj = storage.head(video.object_key)
    if obj is None:
        raise HTTPException(400, "Object not found in storage")
    if obj["ContentLength"] != video.declared_size:
        raise HTTPException(400, "Uploaded size does not match declared size")

    # Verify and enqueue in one transaction: no verified video without a job, and vice versa.
    video.status = VideoStatus.uploaded
    video.object_etag = obj["ETag"]
    job = Job(video_id=video.id)
    db.add(job)
    db.commit()
    return job
