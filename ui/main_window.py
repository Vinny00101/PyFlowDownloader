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


class MainWindow(QMainWindow):
    """Janela principal: compoe widgets e conecta fluxos da UI."""

    def __init__(
        self,
        manager: ThreadManager = None,
        settings=None,
        settings_path=None,  # Alerta de não uso
        history=None,        # Alerta de não uso
        signals=None,        # Alerta de não uso
    ) -> None:
        super().__init__()
        self._manager = manager
        self._settings = settings or {"theme": "dark"}#Assim, mesmo que ninguém passe settings, o app sempre terá um tema padrão.
        self._settings_path = settings_path
        self._history = history
        self._signals = signals

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
        )

        self._shutdown_controller = ShutdownController(
            manager=self._manager,
            queue_panel=self.view.queue_panel,
        )

        #lê o tema e aplica o estilo ao app
        theme_name = self._settings.get("theme", "dark") if self._settings else "dark"
        colors = get_theme(theme_name)
        self.setStyleSheet(colors)#
        self._connect_signals()
        self.view.queue_panel.start_polling(self._manager)

    def _connect_signals(self) -> None:
        self.view.input_bar.download_requested.connect(self._on_download_requested)
        self.view.queue_panel.cancel_requested.connect(
            self._download_controller.confirm_cancel
        )
        self.view.queue_panel.status_changed.connect(self._update_status_bar)
        self.view.queue_panel.error_reported.connect(self._log_download_error)
        self.view.history_panel.clear_requested.connect(
            self._history_controller.clear_history
        )
        self.view.settings_btn.clicked.connect(
            self._settings_controller.open_settings
        )
        self.view.tabs.currentChanged.connect(self._on_tab_changed)
        
        # lê o tema e aplica o estilo ao app
    def apply_theme(self, theme_name: str) -> None:
        if self._settings is not None:
            self._settings["theme"] = theme_name
        colors = get_theme(theme_name)
        self.setStyleSheet(colors)

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
            (self.view.tabs.currentChanged, self._on_tab_changed),
        ):
            try:
                signal.disconnect(slot)
            except TypeError:
                pass

    def closeEvent(self, event):
        self._disconnect_signals()
        self._shutdown_controller.shutdown()
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
