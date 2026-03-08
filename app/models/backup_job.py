import enum
from datetime import datetime
from sqlalchemy import String, DateTime, Enum, ForeignKey, BigInteger, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BackupStatus(str, enum.Enum):
    """
    Mirrors real-world backup job lifecycle states.
    Inheriting from str makes JSON serialization seamless.
    """
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    WARNING = "WARNING"  # completed with non-critical issues (e.g. skipped files)


class BackupJob(Base):
    __tablename__ = "backup_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    status: Mapped[BackupStatus] = mapped_column(
        Enum(BackupStatus, name="backupstatus"), nullable=False, default=BackupStatus.PENDING
    )
    source: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g. "Microsoft 365", "Salesforce"
    size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    client: Mapped["Client"] = relationship("Client", back_populates="backup_jobs")  # noqa: F821
