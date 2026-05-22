from ui.protocols import DownloadManagerProtocol
from ui.widgets.panels import QueuePanel


class ShutdownController:
    """Centraliza limpeza de sinais, timers e tarefas em execução."""

    def __init__(
        self,
        manager: DownloadManagerProtocol | None,
        queue_panel: QueuePanel,
    ) -> None:
        self._manager = manager
        self._queue_panel = queue_panel

    def shutdown(self) -> None:
        self._queue_panel.stop()
        if self._manager:
            for task in self._manager.list_tasks():
                if task.status in ("running", "pending"):
                    self._manager.cancel(task.task_id)
