import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth import current_user
from app.db import get_db
from app.models import Incident, Job, Review, Video
from app.schemas import IncidentOut, JobOut, ReviewIn

router = APIRouter(tags=["jobs"])

Db = Annotated[Session, Depends(get_db)]
User = Annotated[str, Depends(current_user)]


def _owned_job(db: Session, job_id: uuid.UUID, user: str) -> Job:
    job = db.scalar(
        select(Job).join(Video).where(Job.id == job_id, Video.owner_id == user)
    )
    if job is None:
        raise HTTPException(404, "Job not found")
    return job


@router.get("/jobs", response_model=list[JobOut])
def list_jobs(db: Db, user: User, limit: int = 50):
    return db.scalars(
        select(Job)
        .join(Video)
        .where(Video.owner_id == user)
        .order_by(Job.created_at.desc())
        .limit(min(limit, 200))
    ).all()


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: uuid.UUID, db: Db, user: User):
    return _owned_job(db, job_id, user)


@router.get("/jobs/{job_id}/incidents", response_model=list[IncidentOut])
def list_incidents(job_id: uuid.UUID, db: Db, user: User):
    _owned_job(db, job_id, user)
    incidents = db.scalars(
        select(Incident)
        .where(Incident.job_id == job_id)
        .options(selectinload(Incident.reviews))
        .order_by(Incident.start_ms)
    ).all()
    out = []
    for inc in incidents:
        item = IncidentOut.model_validate(inc)
        if inc.reviews:
            item.latest_decision = max(inc.reviews, key=lambda r: r.created_at).decision
        out.append(item)
    return out


@router.post("/incidents/{incident_id}/review", status_code=201)
def review_incident(incident_id: uuid.UUID, body: ReviewIn, db: Db, user: User):
    incident = db.scalar(
        select(Incident)
        .join(Job)
        .join(Video)
        .where(Incident.id == incident_id, Video.owner_id == user)
    )
    if incident is None:
        raise HTTPException(404, "Incident not found")
    review = Review(incident_id=incident.id, reviewer_id=user, decision=body.decision, note=body.note)
    db.add(review)
    db.commit()
    return {"id": review.id, "decision": review.decision}
