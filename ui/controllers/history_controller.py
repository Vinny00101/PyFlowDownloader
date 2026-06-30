from PySide6.QtCore import QObject, Slot

from services import DesktopApiService
from ui.protocols import DownloadManagerProtocol
from ui.widgets.panels import HistoryPanel


class HistoryController(QObject):
    """Coordena ações da aba de histórico."""

    def __init__(
        self,
        manager: DownloadManagerProtocol | None,
        history_panel: HistoryPanel,
        api_service: DesktopApiService | None = None,
    ) -> None:
        super().__init__(history_panel)
        self._manager = manager
        self._history_panel = history_panel
        self._api_service = api_service

    @Slot()
    def clear_history(self) -> None:
        if self._api_service is not None:
            self._api_service.clear_downloads()
        if self._manager:
            self._manager.clear_terminal_tasks()
        self.refresh()

    def refresh(self) -> None:
        if self._api_service is not None and self._api_service.health_check():
            self._history_panel.refresh(self._api_service.list_downloads())
            return
        if not self._manager:
            self._history_panel.refresh([])
            return
        self._history_panel.refresh(self._manager.list_tasks())
