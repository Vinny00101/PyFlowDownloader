from __future__ import annotations

from PySide6.QtCore import QObject, Slot

from core.thread_manager import ThreadManager
from ui.controllers import DownloadController, HistoryController
from ui.protocols import LoggerProtocol
from ui.styles.themes import get_theme
from ui.views import MainView


class MainWindowSlots(QObject):
    """Slots da janela principal, separados da montagem da MainWindow."""

    def __init__(
        self,
        main_window,
        view: MainView,
        thread_manager: ThreadManager | None,
        logger: LoggerProtocol,
        download_controller: DownloadController,
        history_controller: HistoryController,
    ) -> None:
        super().__init__(main_window)
        self._main_window = main_window
        self._view = view
        self._thread_manager = thread_manager
        self._logger = logger
        self._download_controller = download_controller
        self._history_controller = history_controller

    @Slot(str)
    def slot_apply_theme(self, theme_name: str) -> None:
        self._main_window.setStyleSheet(get_theme(theme_name))

    @Slot(str, str, bool, str, str)
    def slot_download_requested(
        self,
        url: str,
        format_spec: str,
        is_audio: bool,
        download_format: str,
        quality: str,
    ) -> None:
        self._download_controller.add_download(
            url,
            format_spec,
            is_audio,
            download_format,
            quality,
        )
        self._view.tabs.setCurrentIndex(0)

    @Slot(int)
    def slot_tab_changed(self, index: int) -> None:
        if index == self._view.history_tab_idx:
            self._history_controller.refresh()
        elif index == self._view.logs_tab_idx and hasattr(self._main_window, "_refresh_app_logs"):
            self._main_window._refresh_app_logs()

    @Slot(str)
    def slot_download_path_changed(self, path: str) -> None:
        if self._thread_manager is None:
            return
        self._thread_manager.set_output_dir(path)
        self._logger.log(f"Caminho foi alterado para: {path}")

    @Slot(str)
    def slot_download_format_changed(self, download_format: str) -> None:
        self._view.input_bar.apply_defaults(default_format=download_format)
        self._logger.log(
            f"O formato padrão de vídeo foi modificado para: {download_format}"
        )

    @Slot(str)
    def slot_download_quality_changed(self, quality: str) -> None:
        self._view.input_bar.apply_defaults(default_quality=quality)
        self._logger.log(f"Qualidade padrão foi modificada para: {quality}")

    @Slot(int)
    def slot_concurrent_downloads_changed(self, max_workers: int) -> None:
        if self._thread_manager is None:
            return
        message = self._thread_manager.set_max_workers(max_workers)
        if message is not None:
            self._logger.log(message)
            return
        self._logger.log(
            "Quantidade de downloads executando ao mesmo tempo "
            f"foi modificada para: {max_workers}"
        )

    @Slot(int, str)
    def slot_download_error_reported(self, task_id: int, message: str) -> None:
        self._logger.log(f"Erro no download #{task_id}: {message}")

    @Slot(int, int, int)
    def slot_status_changed(self, total: int, active: int, queued: int) -> None:
        self._view.status_bar_label.setText(
            f"{total} downloads · {active} ativos · {queued} na fila"
        )
