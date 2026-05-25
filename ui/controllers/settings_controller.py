import sys

from PySide6.QtCore import QObject, QProcess, Slot
from PySide6.QtWidgets import QMessageBox, QWidget

from ui.protocols import LoggerProtocol
from ui.widgets.settings_dialog import SettingsDialog


SETTINGS_SECTIONS = [
    ("Aparência", ["Tema"]),
    ("Downloads", ["Pasta padrão", "Formato padrão", "Qualidade padrão", "Downloads simultâneos"]),
    ("Ferramentas", ["Caminho do ffmpeg", "Testar ffmpeg", "Versão do yt-dlp", "Atualizar yt-dlp"]),
    ("YouTube", ["Cookies do navegador"]),
]


class SettingsController(QObject):
    """Abre a tela de configurações e executa ações de ferramentas."""

    def __init__(
        self,
        parent_widget: QWidget,
        logger: LoggerProtocol | None = None,
    ) -> None:
        super().__init__(parent_widget)
        self._parent_widget = parent_widget
        self._logger = logger
        self._update_process: QProcess | None = None

    @Slot()
    def open_settings(self) -> None:
        dialog = SettingsDialog(parent=self._parent_widget, sections=SETTINGS_SECTIONS)
        dialog.update_ytdlp_requested.connect(self.update_ytdlp)
        dialog.exec()

    @Slot()
    def update_ytdlp(self) -> None:
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
