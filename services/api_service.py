from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

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


class DesktopApiService:
    """Camada de integração com a API.

    Por enquanto roda em modo teste, sem chamadas HTTP. A UI já chama esta
    camada para que a troca futura para API real fique concentrada aqui.
    """

    def __init__(self, base_url: str = "http://127.0.0.1:5000", fake_mode: bool = True) -> None:
        self.base_url = base_url.rstrip("/")
        self.fake_mode = fake_mode
        self.routes = api_routes
        self._logs = AppLogStore()
        self._downloads: dict[int, DownloadRecord] = {}
        self._next_download_id = 1

    def health_check(self) -> bool:
        if self.fake_mode:
            return True
        return False

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
        return sorted(self._downloads.values(), key=lambda item: item.created_at, reverse=True)

    def clear_downloads(self) -> None:
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
        return self._logs.add(
            event_type,
            status=status,
            message=message,
            download_id=download_id,
            error_message=error_message,
        )

    def list_logs(self) -> list[AppLogEntry]:
        return self._logs.list_logs()

    def clear_logs(self) -> None:
        self._logs.clear()
