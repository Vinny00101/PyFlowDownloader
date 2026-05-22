import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class DownloadTask:
    task_id: int
    url: str
    destino: str = ""
    title: str = ""
    status: str = "pending"
    progress: float = 0.0
    speed: str = ""
    eta: str = ""
    file_path: Optional[Path] = None
    error_msg: str = ""
    format_spec: str = "best"
    output_template: str = "%(title)s.%(ext)s"
    audio: bool = False
    finished_at: Optional[datetime] = None
    total_bytes: int = 0
    avg_speed_kbps: float = 0.0
    stop_event: threading.Event = field(default_factory=threading.Event)


class ThreadManager:
    """Gerencia downloads paralelos com ThreadPoolExecutor + yt-dlp."""

    def __init__(self, max_workers: int = 3, output_dir: str = "downloads"):
        self.max_workers = max_workers
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._tasks: dict[int, DownloadTask] = {}
        self._futures: dict[int, Future] = {}
        self._lock = threading.Lock()
        self._next_id = 0
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(exist_ok=True)
        self._process_manager = None

    def _get_process_manager(self):
        if self._process_manager is None:
            from core.process_manager import ProcessManager
            self._process_manager = ProcessManager(output_dir=str(self._output_dir))
        return self._process_manager

    def submit(
        self,
        url: str,
        destino: str = "",
        format_spec: str = "best",
        audio: bool = False,
    ) -> int:
        with self._lock:
            task_id = self._next_id
            self._next_id += 1
            task = DownloadTask(
                task_id=task_id,
                url=url,
                destino=destino or str(self._output_dir),
                format_spec=format_spec,
                audio=audio,
            )
            self._tasks[task_id] = task

        future = self._executor.submit(self._run_download, task)
        self._futures[task_id] = future
        future.add_done_callback(lambda f: self._on_done(task_id))
        return task_id

    def cancel(self, task_id: int) -> bool:
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            task.stop_event.set()
            task.status = "cancelled"
            task.finished_at = datetime.now()

        future = self._futures.get(task_id)
        if future and not future.done():
            return future.cancel()
        return True

    def pause(self, task_id: int):
        # Alerta de não uso
        with self._lock:
            task = self._tasks.get(task_id)
            if task and task.status == "running":
                task.stop_event.set()
                task.status = "paused"

    def shutdown(self, wait: bool = True):
        self._executor.shutdown(wait=wait)

    def get_task(self, task_id: int) -> Optional[DownloadTask]:
        return self._tasks.get(task_id)

    def list_tasks(self) -> list[DownloadTask]:
        with self._lock:
            return list(self._tasks.values())

    def active_count(self) -> int:
        # Alerta de não uso
        return sum(1 for t in self._tasks.values() if t.status == "running")

    def queued_count(self) -> int:
        # Alerta de não uso
        return sum(1 for t in self._tasks.values() if t.status == "pending")

    def clear_terminal_tasks(self) -> None:
        """Remove todas as tarefas com status terminal (completed, error, cancelled)."""
        with self._lock:
            to_remove = [
                tid
                for tid, t in self._tasks.items()
                if t.status in ("completed", "error", "cancelled")
            ]
            for tid in to_remove:
                del self._tasks[tid]
                self._futures.pop(tid, None)

    def _run_download(self, task: DownloadTask):
        pm = self._get_process_manager()

        def progress_hook(d):
            if task.stop_event.is_set():
                raise Exception("Cancelado pelo usuário")

            if d["status"] == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                downloaded = d.get("downloaded_bytes", 0)
                task.progress = (downloaded / total * 100) if total else 0
                task.speed = _fmt_speed(d.get("speed", 0))
                task.total_bytes = total
                eta = d.get("eta")
                task.eta = _fmt_eta(eta) if eta is not None else ""

            elif d["status"] == "finished":
                task.progress = 100.0

        task.status = "running"
        try:
            if task.audio:
                result = pm.download_audio(
                    url=task.url,
                    output_template=task.output_template,
                    format_spec=task.format_spec,
                    progress_hook=progress_hook,
                )
            else:
                result = pm.download(
                    url=task.url,
                    output_template=task.output_template,
                    format_spec=task.format_spec,
                    progress_hook=progress_hook,
                )
            task.file_path = result
            if not task.stop_event.is_set():
                task.status = "completed"
                task.progress = 100.0
                task.finished_at = datetime.now()
        except Exception as e:
            if not task.stop_event.is_set():
                task.status = "error"
                task.error_msg = str(e)
                task.finished_at = datetime.now()

    def _on_done(self, task_id: int):
        task = self._tasks.get(task_id)
        if not task:
            return
        if task.status in ("cancelled", "paused"):
            return
        future = self._futures.get(task_id)
        if future is None:
            return
        try:
            future.result()
        except Exception as e:
            if not task.stop_event.is_set():
                task.status = "error"
                task.error_msg = str(e)


def _fmt_speed(bytes_per_sec) -> str:
    if not bytes_per_sec:
        return ""
    bps = float(bytes_per_sec)
    if bps >= 1_000_000:
        return f"{bps / 1_000_000:.1f} MB/s"
    if bps >= 1_000:
        return f"{bps / 1_000:.1f} KB/s"
    return f"{bps:.0f} B/s"


def _fmt_eta(secs) -> str:
    secs = int(secs)
    if secs < 60:
        return f"{secs}s"
    if secs < 3600:
        return f"{secs // 60}m {secs % 60}s"
    return f"{secs // 3600}h {(secs % 3600) // 60}m"
