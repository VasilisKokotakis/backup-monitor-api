from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.backup_job import BackupJob, BackupStatus
from app.models.client import Client
from app.models.user import User
from app.schemas.backup_job import BackupJobCreate, BackupJobOut, BackupSummary


router = APIRouter(tags=["backups"])


@router.get("/clients/{client_id}/backups", response_model=list[BackupJobOut])
def list_backups(
    client_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[BackupJob]:
    if not db.get(Client, client_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return (
        db.query(BackupJob)
        .filter(BackupJob.client_id == client_id)
        .order_by(BackupJob.created_at.desc())
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
    _: User = Depends(get_current_user),
) -> BackupJob:
    if not db.get(Client, client_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    job = BackupJob(client_id=client_id, **payload.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/backups/summary", response_model=BackupSummary)
def backup_summary(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> BackupSummary:
    total = db.query(func.count(BackupJob.id)).scalar() or 0

    counts = db.query(BackupJob.status, func.count(BackupJob.id)).group_by(BackupJob.status).all()
    by_status: dict[BackupStatus, int] = {status: count for status, count in counts}

    latest_failure = (
        db.query(BackupJob)
        .filter(BackupJob.status == BackupStatus.FAILED)
        .order_by(BackupJob.created_at.desc())
        .first()
    )

    return BackupSummary(total=total, by_status=by_status, latest_failure=latest_failure)
