from datetime import datetime
from pydantic import BaseModel, Field

from app.models.backup_job import BackupStatus


class BackupJobCreate(BaseModel):
    source: str = Field(min_length=1, max_length=255)
    status: BackupStatus = BackupStatus.PENDING
    size_bytes: int | None = None
    error_message: str | None = Field(default=None, max_length=1000)


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
