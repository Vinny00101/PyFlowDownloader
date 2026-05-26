from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow

from core.settings_manager import SettingsManager
from core.thread_manager import ThreadManager
from ui.controllers import (
    DownloadController,
    HistoryController,
    SettingsController,
    ShutdownController,
)
from ui.slots import MainWindowSlots
from ui.utils.signals import connect_many, disconnect_many
from ui.views import MainView


class MainWindow(QMainWindow):
    """Janela principal: monta dependências, view e wiring de sinais."""

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
        self._slots = MainWindowSlots(
            main_window=self,
            view=self.view,
            thread_manager=self._manager,
            logger=self.view.log_widget,
            download_controller=self._download_controller,
            history_controller=self._history_controller,
        )

        self._slots.slot_apply_theme(
            self._settings_manager.get("appearance.theme", "dark")
        )
        self.view.input_bar.apply_defaults(
            default_format=self._settings_manager.get("downloads.default_format", "mp4"),
            default_quality=self._settings_manager.get("downloads.default_quality", "720p"),
        )
        self._connect_signals()
        self.view.queue_panel.start_polling(self._manager)

    def _signal_connections(self):
        return (
            (self.view.input_bar.download_requested, self._slots.slot_download_requested),
            (self.view.queue_panel.cancel_requested, self._download_controller.confirm_cancel),
            (self.view.queue_panel.status_changed, self._slots.slot_status_changed),
            (self.view.queue_panel.error_reported, self._slots.slot_download_error_reported),
            (self.view.history_panel.clear_requested, self._history_controller.clear_history),
            (self.view.settings_btn.clicked, self._settings_controller.open_settings),
            (self._settings_controller.download_path_changed, self._slots.slot_download_path_changed),
            (self._settings_controller.download_format_changed, self._slots.slot_download_format_changed),
            (self._settings_controller.download_quality_changed, self._slots.slot_download_quality_changed),
            (self._settings_controller.concurrent_downloads_changed, self._slots.slot_concurrent_downloads_changed),
            (self._settings_controller.theme_changed, self._slots.slot_apply_theme),
            (self.view.tabs.currentChanged, self._slots.slot_tab_changed),
        )

    def _connect_signals(self) -> None:
        connect_many(self._signal_connections())

    def _disconnect_signals(self) -> None:
        disconnect_many(self._signal_connections())

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
