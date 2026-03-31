import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.backup_job import BackupJob, BackupStatus
from app.models.client import Client
from app.models.user import User
from app.schemas.backup_job import BackupJobCreate, BackupJobOut, BackupSummary


logger = logging.getLogger(__name__)

router = APIRouter(tags=["backups"])


def _get_owned_client(client_id: int, current_user: User, db: Session) -> Client:
    """Return the client if it exists and belongs to current_user, else 404."""
    client = db.get(Client, client_id)
    if not client or client.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return client


@router.get("/clients/{client_id}/backups", response_model=list[BackupJobOut])
def list_backups(
    client_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[BackupJob]:
    _get_owned_client(client_id, current_user, db)
    return (
        db.query(BackupJob)
        .filter(BackupJob.client_id == client_id)
        .order_by(BackupJob.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.post(
    "/clients/{client_id}/backups",
    response_model=BackupJobOut,
    status_code=status.HTTP_201_CREATED,
)
def create_backup(
    client_id: int,
    payload: BackupJobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BackupJob:
    _get_owned_client(client_id, current_user, db)
    now = datetime.now(timezone.utc)
    started_at = now if payload.status == BackupStatus.RUNNING else None
    finished_at = now if payload.status in {BackupStatus.SUCCESS, BackupStatus.FAILED, BackupStatus.WARNING} else None
    job = BackupJob(
        client_id=client_id,
        started_at=started_at,
        finished_at=finished_at,
        **payload.model_dump(),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    logger.info("Backup job created: id=%d client_id=%d status=%s", job.id, client_id, job.status.value)
    return job


@router.get("/backups/summary", response_model=BackupSummary)
def backup_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BackupSummary:
    owned_client_ids = (
        db.query(Client.id).filter(Client.owner_id == current_user.id)
    )
    total = (
        db.query(func.count(BackupJob.id))
        .filter(BackupJob.client_id.in_(owned_client_ids))
        .scalar() or 0
    )

    counts = (
        db.query(BackupJob.status, func.count(BackupJob.id))
        .filter(BackupJob.client_id.in_(owned_client_ids))
        .group_by(BackupJob.status)
        .all()
    )
    by_status: dict[BackupStatus, int] = {s: count for s, count in counts}

    latest_failure = (
        db.query(BackupJob)
        .filter(
            BackupJob.client_id.in_(owned_client_ids),
            BackupJob.status == BackupStatus.FAILED,
        )
        .order_by(BackupJob.created_at.desc())
        .first()
    )

    return BackupSummary(total=total, by_status=by_status, latest_failure=latest_failure)
