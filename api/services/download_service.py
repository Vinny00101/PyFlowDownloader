from datetime import datetime

from api.models import Download, db


class DownloadService:
    @staticmethod
    def create(data: dict) -> Download:
        download = Download(
            local_task_id=data.get("local_task_id"),
            url=data["url"],
            title=data.get("title"),
            status=data.get("status") or "pending",
            download_format=data.get("download_format"),
            quality=data.get("quality"),
            format_spec=data.get("format_spec"),
            is_audio=bool(data.get("is_audio", False)),
            file_path=data.get("file_path"),
            error_message=data.get("error_message"),
            total_bytes=int(data.get("total_bytes") or 0),
            avg_speed_kbps=float(data.get("avg_speed_kbps") or 0),
            progress=float(data.get("progress") or 0),
            started_at=_parse_datetime(data.get("started_at")),
            finished_at=_parse_datetime(data.get("finished_at")),
            duration_seconds=float(data.get("duration_seconds") or 0),
            app_version=data.get("app_version"),
        )
        db.session.add(download)
        db.session.commit()
        return download

    @staticmethod
    def list(limit: int = 50, status: str | None = None) -> list[Download]:
        query = Download.query
        if status:
            query = query.filter(Download.status == status)
        return query.order_by(Download.created_at.desc()).limit(limit).all()

    @staticmethod
    def get(download_id: int) -> Download | None:
        return db.session.get(Download, download_id)

    @staticmethod
    def update(download_id: int, data: dict) -> Download | None:
        download = DownloadService.get(download_id)
        if download is None:
            return None

        allowed_fields = {
            "local_task_id",
            "url",
            "title",
            "status",
            "download_format",
            "quality",
            "format_spec",
            "is_audio",
            "file_path",
            "error_message",
            "total_bytes",
            "avg_speed_kbps",
            "progress",
            "started_at",
            "finished_at",
            "duration_seconds",
            "app_version",
        }

        for field in allowed_fields:
            if field not in data:
                continue
            value = data[field]
            if field in {"started_at", "finished_at"}:
                value = _parse_datetime(value)
            setattr(download, field, value)

        db.session.commit()
        return download

    @staticmethod
    def clear() -> int:
        count = Download.query.delete()
        db.session.commit()
        return count


def _parse_datetime(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
