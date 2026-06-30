from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class AppLog(db.Model):
    __tablename__ = "app_logs"

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(80), nullable=False, index=True)
    status = db.Column(db.String(40), nullable=True, index=True)
    message = db.Column(db.String(255), nullable=True)
    url = db.Column(db.Text, nullable=True)
    download_format = db.Column(db.String(20), nullable=True)
    quality = db.Column(db.String(20), nullable=True)
    file_path = db.Column(db.Text, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    app_version = db.Column(db.String(20), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "event_type": self.event_type,
            "status": self.status,
            "message": self.message,
            "url": self.url,
            "download_format": self.download_format,
            "quality": self.quality,
            "file_path": self.file_path,
            "error_message": self.error_message,
            "app_version": self.app_version,
            "created_at": self.created_at.isoformat(),
        }
