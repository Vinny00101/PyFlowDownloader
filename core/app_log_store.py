from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class AppLogEntry:
    event_type: str
    status: str = ""
    message: str = ""
    download_id: int | None = None
    error_message: str = ""
    created_at: datetime = field(default_factory=datetime.now)


class AppLogStore:
    """Armazena logs em memória até a integração com a API ficar pronta."""

    def __init__(self) -> None:
        self._logs: list[AppLogEntry] = []

    def add(
        self,
        event_type: str,
        *,
        status: str = "",
        message: str = "",
        download_id: int | None = None,
        error_message: str = "",
    ) -> AppLogEntry:
        entry = AppLogEntry(
            event_type=event_type,
            status=status,
            message=message,
            download_id=download_id,
            error_message=error_message,
        )
        self._logs.append(entry)
        return entry

    def list_logs(self) -> list[AppLogEntry]:
        return list(reversed(self._logs))

    def clear(self) -> None:
        self._logs.clear()
