import sys
from typing import Any

from PySide6.QtCore import QObject, QProcess, Signal, Slot
from PySide6.QtWidgets import QMessageBox, QWidget

from ui.protocols import LoggerProtocol
from ui.widgets.settings_dialog import SettingsDialog
from core.settings_manager import SettingsManager


SETTINGS_SECTIONS = [
    ("Aparência", ["Tema"]),
    ("Downloads", ["Pasta padrão", "Formato padrão", "Qualidade padrão", "Downloads simultâneos"]),
    ("Ferramentas", [ "Versão do yt-dlp", "Atualizar yt-dlp"]),
    ##("YouTube", ["Cookies do navegador"]),
]


class SettingsController(QObject):
    """Abre a tela de configurações e executa ações de ferramentas."""

    download_format_changed = Signal(str)
    download_quality_changed = Signal(str)
    download_path_changed = Signal(str)
    concurrent_downloads_changed = Signal(int)
    theme_changed = Signal(str)

    def __init__(
        self,
        parent_widget: QWidget,
        logger: LoggerProtocol | None = None,
        settings_manager: SettingsManager | None = None,
    ) -> None:
        super().__init__(parent_widget)
        self._parent_widget = parent_widget
        self._logger = logger
        self._update_process: QProcess | None = None
        self._settings_manager = settings_manager or SettingsManager()

    @Slot()
    def open_settings(self) -> None:
        dialog = SettingsDialog(
            parent=self._parent_widget,
            sections=SETTINGS_SECTIONS,
            settings_manager=self._settings_manager,
        )
        dialog.download_format_changed.connect(self.download_format_changed.emit)
        dialog.download_quality_changed.connect(self.download_quality_changed.emit)
        dialog.concurrent_downloads_changed.connect(self.concurrent_downloads_changed.emit)
        dialog.download_path_changed.connect(self.download_path_changed.emit)
        dialog.theme_changed.connect(self.theme_changed.emit)
        dialog.update_ytdlp_requested.connect(self.update_ytdlp)
        dialog.exec()

    @Slot()
    def update_ytdlp(self) -> None:
        if getattr(sys, "frozen", False):
            QMessageBox.information(
                self._parent_widget,
                "Atualização do yt-dlp",
                "Na versão empacotada do aplicativo, o yt-dlp é atualizado junto com uma nova versão do PyFlowDownloader.\n"
                "Por favor, baixe a última versão do aplicativo em nossa página de releases."
            )
            return
        
        if self._update_process is not None:
            QMessageBox.information(
                self._parent_widget,
                "Atualização em andamento",
                "O yt-dlp já está sendo atualizado.",
            )
            return

        self._log("Atualizando yt-dlp...")
        process = QProcess(self)
        process.setProgram(sys.executable)
        process.setArguments(["-m", "pip", "install", "--upgrade", "yt-dlp"])
        process.readyReadStandardOutput.connect(self._log_update_stdout)
        process.readyReadStandardError.connect(self._log_update_stderr)
        process.finished.connect(self._on_update_finished)
        process.errorOccurred.connect(self._on_update_error)
        self._update_process = process
        process.start()

    def _log_update_stdout(self) -> None:
        self._log_process_output(is_error=False)

    def _log_update_stderr(self) -> None:
        self._log_process_output(is_error=True)

    def _log_process_output(self, is_error: bool) -> None:
        if self._update_process is None:
            return
        data = (
            self._update_process.readAllStandardError()
            if is_error
            else self._update_process.readAllStandardOutput()
        )
        text = bytes(data).decode(errors="replace").strip()
        if text:
            self._log(text)

    def _on_update_finished(self, exit_code: int, _exit_status) -> None:
        self._update_process = None
        if exit_code == 0:
            self._log("yt-dlp atualizado com sucesso. Reinicie o aplicativo se a versão não mudar imediatamente.")
            QMessageBox.information(
                self._parent_widget,
                "yt-dlp atualizado",
                "Atualização concluída com sucesso.",
            )
            return

        self._log(f"Erro ao atualizar yt-dlp. Código de saída: {exit_code}")
        QMessageBox.warning(
            self._parent_widget,
            "Falha ao atualizar",
            "Não foi possível atualizar o yt-dlp. Veja os logs para detalhes.",
        )

    def _on_update_error(self, error) -> None:
        self._update_process = None
        self._log(f"Erro ao iniciar atualização do yt-dlp: {error}")

    def _log(self, message: str) -> None:
        if self._logger is not None:
            self._logger.log(message)

    def get_settings(self, key_path: str, default: Any = None):
        return self._settings_manager.get(key_path, default)

    def set_settings(self, key_path: str, value: Any) -> None:
        self._settings_manager.set(key_path, value)
        self._settings_manager.save()
