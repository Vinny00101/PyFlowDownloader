import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from core.app_info import APP_VERSION
from core.app_log_store import AppLogEntry, AppLogStore
from . import api_routes


@dataclass(slots=True)
class DownloadRecord:
    id: int
    local_task_id: int | None
    url: str
    title: str = ""
    status: str = "pending"
    download_format: str = ""
    quality: str = ""
    format_spec: str = ""
    is_audio: bool = False
    file_path: str = ""
    error_message: str = ""
    total_bytes: int = 0
    avg_speed_kbps: float = 0.0
    progress: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    finished_at: datetime | None = None
    duration_seconds: float = 0.0
    app_version: str = APP_VERSION

    @property
    def error_msg(self) -> str:
        return self.error_message

    @property
    def audio(self) -> bool:
        return self.is_audio


class DesktopApiService:
    """Camada de integração com a API.

    Por enquanto roda em modo teste, sem chamadas HTTP. A UI já chama esta
    camada para que a troca futura para API real fique concentrada aqui.
    """

    def __init__(self, base_url: str = "http://127.0.0.1:5000", fake_mode: bool = False) -> None:
        self.base_url = base_url.rstrip("/")
        self.fake_mode = fake_mode
        self.routes = api_routes
        self._logs = AppLogStore()
        self._downloads: dict[int, DownloadRecord] = {}
        self._next_download_id = 1

    def health_check(self) -> bool:
        if self.fake_mode:
            return True
        return self._request("GET", api_routes.API_HEALTH) is not None

    def create_download(
        self,
        *,
        local_task_id: int | None,
        url: str,
        title: str = "",
        status: str = "pending",
        download_format: str = "",
        quality: str = "",
        format_spec: str = "",
        is_audio: bool = False,
    ) -> DownloadRecord:
        payload = {
            "local_task_id": local_task_id,
            "url": url,
            "title": title,
            "status": status,
            "download_format": download_format,
            "quality": quality,
            "format_spec": format_spec,
            "is_audio": is_audio,
            "app_version": APP_VERSION,
        }
        if not self.fake_mode:
            data = self._request("POST", api_routes.API_DOWNLOADS, payload)
            if data is not None:
                record = _download_from_dict(data)
                self._downloads[record.id] = record
                return record

        record = DownloadRecord(
            id=self._next_download_id,
            local_task_id=local_task_id,
            url=url,
            title=title,
            status=status,
            download_format=download_format,
            quality=quality,
            format_spec=format_spec,
            is_audio=is_audio,
        )
        self._downloads[record.id] = record
        self._next_download_id += 1
        return record

    def update_download(
        self,
        download_id: int,
        **changes,
    ) -> DownloadRecord | None:
        if not self.fake_mode:
            payload = _json_ready(changes)
            data = self._request(
                "PATCH",
                api_routes.API_DOWNLOAD_BY_ID.format(download_id=download_id),
                payload,
            )
            if data is not None:
                record = _download_from_dict(data)
                self._downloads[record.id] = record
                return record

        record = self._downloads.get(download_id)
        if record is None:
            return None

        for key, value in changes.items():
            if hasattr(record, key):
                if isinstance(value, Path):
                    value = str(value)
                setattr(record, key, value)
        return record

    def update_download_by_local_task(
        self,
        local_task_id: int,
        **changes,
    ) -> DownloadRecord | None:
        record = self.get_download_by_local_task(local_task_id)
        if record is None:
            return None
        return self.update_download(record.id, **changes)

    def get_download_by_local_task(self, local_task_id: int) -> DownloadRecord | None:
        for record in self._downloads.values():
            if record.local_task_id == local_task_id:
                return record
        return None

    def list_downloads(self) -> list[DownloadRecord]:
        if not self.fake_mode:
            data = self._request("GET", api_routes.API_DOWNLOADS)
            if isinstance(data, list):
                records = [_download_from_dict(item) for item in data]
                self._downloads = {record.id: record for record in records}
                return records
        return sorted(self._downloads.values(), key=lambda item: item.created_at, reverse=True)

    def clear_downloads(self) -> None:
        if not self.fake_mode:
            self._request("DELETE", api_routes.API_DOWNLOADS)
        self._downloads.clear()

    def create_log(
        self,
        event_type: str,
        *,
        status: str = "",
        message: str = "",
        download_id: int | None = None,
        error_message: str = "",
    ) -> AppLogEntry:
        payload = {
            "event_type": event_type,
            "status": status,
            "message": message,
            "download_id": download_id,
            "error_message": error_message,
            "app_version": APP_VERSION,
        }
        if not self.fake_mode:
            data = self._request("POST", api_routes.API_LOGS, payload)
            if data is not None:
                entry = _log_from_dict(data)
                self._logs.add(
                    entry.event_type,
                    status=entry.status,
                    message=entry.message,
                    download_id=entry.download_id,
                    error_message=entry.error_message,
                )
                return entry

        return self._logs.add(
            event_type,
            status=status,
            message=message,
            download_id=download_id,
            error_message=error_message,
        )

    def list_logs(self) -> list[AppLogEntry]:
        if not self.fake_mode:
            data = self._request("GET", api_routes.API_LOGS)
            if isinstance(data, list):
                return [_log_from_dict(item) for item in data]
        return self._logs.list_logs()

    def clear_logs(self) -> None:
        if not self.fake_mode:
            self._request("DELETE", api_routes.API_LOGS)
        self._logs.clear()

    def _request(self, method: str, route: str, payload: dict | None = None):
        data = None
        headers = {"Content-Type": "application/json"}
        if payload is not None:
            data = json.dumps(_json_ready(payload)).encode("utf-8")

        request = Request(
            f"{self.base_url}{route}",
            data=data,
            headers=headers,
            method=method,
        )

        try:
            with urlopen(request, timeout=3) as response:
                body = response.read().decode("utf-8")
                return json.loads(body) if body else {}
        except (HTTPError, OSError, URLError, json.JSONDecodeError):
            return None


def _download_from_dict(data: dict) -> DownloadRecord:
    return DownloadRecord(
        id=int(data["id"]),
        local_task_id=data.get("local_task_id"),
        url=data.get("url") or "",
        title=data.get("title") or "",
        status=data.get("status") or "pending",
        download_format=data.get("download_format") or "",
        quality=data.get("quality") or "",
        format_spec=data.get("format_spec") or "",
        is_audio=bool(data.get("is_audio", False)),
        file_path=data.get("file_path") or "",
        error_message=data.get("error_message") or "",
        total_bytes=int(data.get("total_bytes") or 0),
        avg_speed_kbps=float(data.get("avg_speed_kbps") or 0),
        progress=float(data.get("progress") or 0),
        created_at=_parse_datetime(data.get("created_at")) or datetime.now(),
        started_at=_parse_datetime(data.get("started_at")),
        finished_at=_parse_datetime(data.get("finished_at")),
        duration_seconds=float(data.get("duration_seconds") or 0),
        app_version=data.get("app_version") or APP_VERSION,
    )


def _log_from_dict(data: dict) -> AppLogEntry:
    return AppLogEntry(
        event_type=data.get("event_type") or "",
        status=data.get("status") or "",
        message=data.get("message") or "",
        download_id=data.get("download_id"),
        error_message=data.get("error_message") or "",
        created_at=_parse_datetime(data.get("created_at")) or datetime.now(),
    )


def _parse_datetime(value) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _json_ready(data: dict) -> dict:
    result = {}
    for key, value in data.items():
        if value is None:
            continue
        if isinstance(value, datetime):
            value = value.isoformat()
        elif isinstance(value, Path):
            value = str(value)
        result[key] = value
    return result
