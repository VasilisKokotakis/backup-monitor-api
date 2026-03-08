from datetime import datetime
from pydantic import BaseModel

from app.models.backup_job import BackupStatus


class BackupJobCreate(BaseModel):
    source: str
    status: BackupStatus = BackupStatus.PENDING
    size_bytes: int | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


class BackupJobOut(BaseModel):
    id: int
    client_id: int
    source: str
    status: BackupStatus
    size_bytes: int | None
    error_message: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class BackupSummary(BaseModel):
    total: int
    by_status: dict[BackupStatus, int]
    latest_failure: BackupJobOut | None
