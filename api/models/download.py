from datetime import datetime, timezone

from .database import db


class Download(db.Model):
    __tablename__ = "downloads"

    id = db.Column(db.Integer, primary_key=True)
    local_task_id = db.Column(db.Integer, nullable=True, index=True)
    url = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(40), nullable=False, default="pending", index=True)
    download_format = db.Column(db.String(20), nullable=True)
    quality = db.Column(db.String(20), nullable=True)
    format_spec = db.Column(db.Text, nullable=True)
    is_audio = db.Column(db.Boolean, nullable=False, default=False)
    file_path = db.Column(db.Text, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    total_bytes = db.Column(db.BigInteger, nullable=False, default=0)
    avg_speed_kbps = db.Column(db.Float, nullable=False, default=0.0)
    progress = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    started_at = db.Column(db.DateTime(timezone=True), nullable=True)
    finished_at = db.Column(db.DateTime(timezone=True), nullable=True)
    duration_seconds = db.Column(db.Float, nullable=False, default=0.0)
    app_version = db.Column(db.String(20), nullable=True)

    logs = db.relationship(
        "AppLog",
        back_populates="download",
        cascade="all, delete-orphan",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "local_task_id": self.local_task_id,
            "url": self.url,
            "title": self.title,
            "status": self.status,
            "download_format": self.download_format,
            "quality": self.quality,
            "format_spec": self.format_spec,
            "is_audio": self.is_audio,
            "file_path": self.file_path,
            "error_message": self.error_message,
            "total_bytes": self.total_bytes,
            "avg_speed_kbps": self.avg_speed_kbps,
            "progress": self.progress,
            "created_at": _isoformat(self.created_at),
            "started_at": _isoformat(self.started_at),
            "finished_at": _isoformat(self.finished_at),
            "duration_seconds": self.duration_seconds,
            "app_version": self.app_version,
        }


def _isoformat(value) -> str | None:
    return value.isoformat() if value is not None else None
