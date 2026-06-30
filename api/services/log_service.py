from api.models import AppLog, db


ALLOWED_EVENT_TYPES = {
    "download_started",
    "download_completed",
    "download_cancelled",
    "download_error",
    "ffmpeg_install_completed",
    "ffmpeg_install_error",
    "ytdlp_updated",
}


class LogService:
    @staticmethod
    def create(data: dict) -> AppLog:
        event_type = str(data.get("event_type", "")).strip()
        if not event_type:
            raise ValueError("event_type é obrigatório")
        if event_type not in ALLOWED_EVENT_TYPES:
            raise ValueError("event_type não é permitido")

        log = AppLog(
            event_type=event_type,
            status=data.get("status"),
            message=data.get("message"),
            download_id=data.get("download_id"),
            error_message=data.get("error_message"),
            app_version=data.get("app_version"),
        )
        db.session.add(log)
        db.session.commit()
        return log

    @staticmethod
    def list(limit: int = 50, event_type: str | None = None) -> list[AppLog]:
        query = AppLog.query
        if event_type:
            query = query.filter(AppLog.event_type == event_type)
        return query.order_by(AppLog.created_at.desc()).limit(limit).all()

    @staticmethod
    def clear() -> int:
        count = AppLog.query.delete()
        db.session.commit()
        return count
