from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QMainWindow

from core.thread_manager import ThreadManager
from ui.controllers import (
    DownloadController,
    HistoryController,
    SettingsController,
    ShutdownController,
)
from ui.layouts import MainView
from ui.styles.themes import get_theme
from core.settings_manager import SettingsManager

class MainWindow(QMainWindow):
    """Janela principal: compoe widgets e conecta fluxos da UI."""

    def __init__(
        self,
        manager: ThreadManager = None,
        settings_manager: SettingsManager | None = None,
    ) -> None:
        super().__init__()
        self._manager = manager
        self._settings_manager = settings_manager or SettingsManager()

        self.setWindowTitle("PyFlowDownloader")
        self.setMinimumSize(960, 700)
        self.resize(1024, 750)

        self.view = MainView.build()
        self.setCentralWidget(self.view.root)
        
        self._download_controller = DownloadController(
            manager=self._manager,
            logger=self.view.log_widget,
            parent_widget=self,
        )
        self._history_controller = HistoryController(
            manager=self._manager,
            history_panel=self.view.history_panel,
        )
        self._settings_controller = SettingsController(
            parent_widget=self,
            logger=self.view.log_widget,
            settings_manager=self._settings_manager,
        )

        self._shutdown_controller = ShutdownController(
            manager=self._manager,
            queue_panel=self.view.queue_panel,
        )

        self.apply_theme(self._settings_manager.get("appearance.theme", "dark"))
        self.view.input_bar.apply_defaults(
            default_format=self._settings_manager.get("downloads.default_format", "mp4"),
            default_quality=self._settings_manager.get("downloads.default_quality", "720p"),
        )
        self._connect_signals()
        self.view.queue_panel.start_polling(self._manager)

    @property
    def settings_manager(self) -> SettingsManager:
        return self._settings_manager

    def _connect_signals(self) -> None:
        self.view.input_bar.download_requested.connect(
            self._on_download_requested
        )
        self.view.queue_panel.cancel_requested.connect(
            self._download_controller.confirm_cancel
        )
        self.view.queue_panel.status_changed.connect(
            self._update_status_bar
        )
        self.view.queue_panel.error_reported.connect(
            self._log_download_error
        )
        self.view.history_panel.clear_requested.connect(
            self._history_controller.clear_history
        )
        self.view.settings_btn.clicked.connect(
            self._settings_controller.open_settings
        )
        self._settings_controller.download_path_changed.connect(
            self._on_download_path_changed
        )
        self._settings_controller.download_format_changed.connect(
            self._on_download_format_changed
        )
        self._settings_controller.download_quality_changed.connect(
            self._on_download_quality_changed
        )
        self._settings_controller.concurrent_downloads_changed.connect(
            self._on_concurrent_downloads_changed
        )
        self._settings_controller.theme_changed.connect(
            self.apply_theme
        )
        self.view.tabs.currentChanged.connect(
            self._on_tab_changed
        )
        
    @Slot(str)
    def apply_theme(self, theme_name: str) -> None:
        self.setStyleSheet(get_theme(theme_name))

    @Slot(str, str, bool)
    def _on_download_requested(
        self,
        url: str,
        format_spec: str,
        is_audio: bool,
    ) -> None:
        self._download_controller.add_download(url, format_spec, is_audio)
        self.view.tabs.setCurrentIndex(0)

    def _on_tab_changed(self, index: int) -> None:
        if index == self.view.history_tab_idx:
            self._history_controller.refresh()

    @Slot(str)
    def _on_download_path_changed(self, path: str) -> None:
        if self._manager is None:
            return
        self._manager.set_output_dir(path)
        self.view.log_widget.log(f"Caminho foi alterado para: {path}")

    @Slot(str)
    def _on_download_format_changed(self, format: str) -> None:
        self.view.input_bar.apply_defaults(default_format=format)
        self.view.log_widget.log(f"O formato padrão de vídeo foi modificada para: {format}")

    @Slot(str)
    def _on_download_quality_changed(self, quality: str):
        self.view.input_bar.apply_defaults(default_quality=quality)
        self.view.log_widget.log(f"Qualidade padrão foi modificada para: {quality}")

    @Slot(int)
    def _on_concurrent_downloads_changed(self, max_workers: int):
        if self._manager is None:
            return
        mensage =  self._manager.set_max_workers(max_workers)
        if mensage is not None:
            self.view.log_widget.log("O numero de workers não foi modificado, pois o numerop informato é negativo")
        else:
            self.view.log_widget.log(f"Quantidade de downloads executando ao mesmo tempo foi modificado: {max_workers}")

    @Slot(int, str)
    def _log_download_error(self, task_id: int, message: str) -> None:
        self.view.log_widget.log(f"Erro no download #{task_id}: {message}")

    @Slot(int, int, int)
    def _update_status_bar(self, total: int, active: int, queued: int) -> None:
        self.view.status_bar_label.setText(
            f"{total} downloads · {active} ativos · {queued} na fila"
        )

    def _disconnect_signals(self) -> None:
        for signal, slot in (
            (self.view.input_bar.download_requested, self._on_download_requested),
            (self.view.queue_panel.cancel_requested, self._download_controller.confirm_cancel),
            (self.view.queue_panel.status_changed, self._update_status_bar),
            (self.view.queue_panel.error_reported, self._log_download_error),
            (self.view.history_panel.clear_requested, self._history_controller.clear_history),
            (self.view.settings_btn.clicked, self._settings_controller.open_settings),
            (self._settings_controller.download_path_changed, self._on_download_path_changed),
            (self._settings_controller.download_format_changed, self._on_download_format_changed),
            (self._settings_controller.download_quality_changed, self._on_download_quality_changed),
            (self._settings_controller.concurrent_downloads_changed, self._on_concurrent_downloads_changed),
            (self._settings_controller.theme_changed, self.apply_theme),
            (self.view.tabs.currentChanged, self._on_tab_changed),
        ):
            try:
                signal.disconnect(slot)
            except TypeError:
                pass

    def closeEvent(self, event):
        self._disconnect_signals()
        self._shutdown_controller.shutdown()
        self._settings_manager.save()
        super().closeEvent(event)

    def toggle_fullscreen(self) -> None:
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def keyPressEvent(self, event_input):
        if event_input.key() == Qt.Key_F11:
            self.toggle_fullscreen()
            event_input.accept()
        else:
            super().keyPressEvent(event_input)
