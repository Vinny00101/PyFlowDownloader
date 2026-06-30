from datetime import datetime
from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class QueueTaskProtocol(Protocol):
    """Contrato mínimo para renderizar uma tarefa na fila."""

    task_id: int
    url: str
    status: str
    progress: float
    speed: str
    eta: str
    error_msg: str | None


@runtime_checkable
class HistoryTaskProtocol(QueueTaskProtocol, Protocol):
    """Contrato mínimo para renderizar uma tarefa no histórico."""

    title: str | None
    file_path: Path | None
    finished_at: datetime | None
    total_bytes: int
    avg_speed_kbps: float
    download_format: str
    quality: str
    duration_seconds: float
