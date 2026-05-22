from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QMessageBox, QWidget

from ui.protocols import DownloadManagerProtocol, LoggerProtocol


class DownloadController(QObject):
    """Executa ações de download acionadas pela UI."""

    def __init__(
        self,
        manager: DownloadManagerProtocol | None,
        logger: LoggerProtocol,
        parent_widget: QWidget,
    ) -> None:
        super().__init__(parent_widget)
        self._manager = manager
        self._logger = logger
        self._parent_widget = parent_widget

    @Slot(str, str, bool)
    def add_download(self, url: str, format_spec: str, is_audio: bool) -> None:
        if not self._manager:
            self._logger.log("Erro: ThreadManager não configurado")
            return

        try:
            self._manager.submit(url=url, format_spec=format_spec, audio=is_audio)
        except ImportError as e:
            QMessageBox.critical(self._parent_widget, "Erro", str(e))
            return
        except Exception as e:
            self._logger.log(f"Erro ao adicionar download: {e}")
            return

        self._logger.log(f"Download adicionado: {url[:60]}")

    @Slot(int)
    def confirm_cancel(self, task_id: int) -> None:
        task = self._manager.get_task(task_id) if self._manager else None
        if not task:
            return

        reply = QMessageBox.question(
            self._parent_widget,
            "Cancelar download",
            f"Tem certeza que deseja cancelar?\n{task.url[:60]}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self._manager.cancel(task_id)
            self._logger.log(f"Download cancelado: {task.url[:50]}")
