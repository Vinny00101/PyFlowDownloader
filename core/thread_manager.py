import os
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from core.yt_dlp_errors import translate_yt_dlp_error


@dataclass
class DownloadTask:
    """Estado de uma tarefa de download exibida pela interface."""

    task_id: int
    url: str
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
    """Gerencia a fila de downloads executada em threads de background."""

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
    
    def set_max_workers(self, max_workers: int) -> str | None:
        """Atualiza o número máximo de workers usados para downloads futuros.
    
        args:
            max_workers: Número desejado de workers (mínimo 1)
            
        returns:
            None se sucesso, mensagem de erro em português se falha
        """
        if max_workers < 1:
            return "Numero de workers nao pode ser menor que 1"
        try:
            cpu_count = os.cpu_count()
            # Se não conseguir detectar, usa valor seguro padrão
            if cpu_count is None:
                system_max = 4
            else:
                # Para tarefas I/O-bound (como downloads), limite razoável é 2x núcleos
                # Mas limitado a 32 para evitar excesso de threads (pode causar thrashing)
                system_max = min(cpu_count * 2, 32)
        except NotImplementedError:
            system_max = 4

        if max_workers > system_max:
            return f"Numero de workers nao pode exceder {system_max} (limite do sistema recomendado)"
        
        with self._lock:
            self._executor.shutdown(wait=False)
            self.max_workers = max_workers
            self._executor = ThreadPoolExecutor(max_workers=max_workers)
        return None

    def set_output_dir(self, output_dir: str | Path) -> None:
        """Atualiza a pasta de saída usada pelos próximos downloads."""
        with self._lock:
            self._output_dir = Path(output_dir)
            self._output_dir.mkdir(parents=True, exist_ok=True)
            self._process_manager = None

    def submit(
        self,
        url: str,
        format_spec: str = "best",
        audio: bool = False,
    ) -> int:
        """Cria uma tarefa e agenda o download no executor.

        A UI chama este método quando o usuário confirma um novo download. A
        tarefa é registrada em `_tasks` para que os widgets possam acompanhar
        o estado, e o trabalho real é enviado para o `ThreadPoolExecutor`.

        Args:
            url: URL que será baixada.
            format_spec: Expressão de formato aceita pelo yt-dlp.
            audio: Define se o fluxo deve baixar somente áudio.

        Returns:
            ID interno da tarefa criada.
        """
        with self._lock:
            task_id = self._next_id
            self._next_id += 1
            task = DownloadTask(
                task_id=task_id,
                url=url,
                format_spec=format_spec,
                audio=audio,
            )
            self._tasks[task_id] = task

        future = self._executor.submit(self._run_download, task)
        self._futures[task_id] = future
        return task_id

    def cancel(self, task_id: int) -> bool:
        """Marca uma tarefa para cancelamento.

        Se a tarefa ainda estiver aguardando no executor, `future.cancel()` pode
        impedir que ela comece. Se ela já estiver rodando, o `stop_event` será
        lido pelo hook de progresso e interromperá o fluxo na próxima atualização
        enviada pelo yt-dlp.
        """
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

    def shutdown(self, wait: bool = True):
        self._executor.shutdown(wait=wait)

    def get_task(self, task_id: int) -> Optional[DownloadTask]:
        return self._tasks.get(task_id)

    def list_tasks(self) -> list[DownloadTask]:
        with self._lock:
            return list(self._tasks.values())

    def clear_terminal_tasks(self) -> None:
        """Remove do histórico interno as tarefas que já terminaram.

        O painel de histórico chama este método ao limpar o histórico. Arquivos
        baixados não são apagados; apenas as referências em memória deixam de
        aparecer na interface.
        """
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
        """Executa o download e atualiza o estado compartilhado da tarefa.

        Este método roda fora da thread principal da interface. O yt-dlp chama
        `progress_hook` várias vezes durante o download; cada chamada atualiza
        progresso, velocidade, tamanho total e ETA. O `QueuePanel` lê esses
        valores periodicamente via `list_tasks()`.
        """

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

        try:
            task.status = "running"
            pm = self._get_process_manager()
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
                task.error_msg = translate_yt_dlp_error(e)
                task.finished_at = datetime.now()


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
