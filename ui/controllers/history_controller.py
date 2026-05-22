from PySide6.QtCore import QObject, Slot

from ui.protocols import DownloadManagerProtocol
from ui.widgets.panels import HistoryPanel


class HistoryController(QObject):
    """Coordena ações da aba de histórico."""

    def __init__(
        self,
        manager: DownloadManagerProtocol | None,
        history_panel: HistoryPanel,
    ) -> None:
        super().__init__(history_panel)
        self._manager = manager
        self._history_panel = history_panel

    @Slot()
    def clear_history(self) -> None:
        if not self._manager:
            return
        self._manager.clear_terminal_tasks()
        self.refresh()

    def refresh(self) -> None:
        if not self._manager:
            return
        self._history_panel.refresh(self._manager.list_tasks())
