from datetime import datetime, timezone

from .database import db


class AppLog(db.Model):
    __tablename__ = "app_logs"

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(80), nullable=False, index=True)
    status = db.Column(db.String(40), nullable=True, index=True)
    message = db.Column(db.String(255), nullable=True)
    download_id = db.Column(db.Integer, db.ForeignKey("downloads.id"), nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    app_version = db.Column(db.String(20), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    download = db.relationship("Download", back_populates="logs")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "event_type": self.event_type,
            "status": self.status,
            "message": self.message,
            "download_id": self.download_id,
            "error_message": self.error_message,
            "app_version": self.app_version,
            "created_at": self.created_at.isoformat(),
        }
