import os
import threading  # NOVO
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QMessageBox, QProgressDialog, QFileDialog # NOVO
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import QMainWindow, QMessageBox, QProgressDialog, QFileDialog
from PySide6.QtGui import QDesktopServices

from core.settings_manager import SettingsManager
from core.thread_manager import ThreadManager
from core.ffmpeg_installer import FFmpegInstaller  # NOVO

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

        # ---- NOVO: instalador do FFmpeg e diálogo de progresso ----
        self.ffmpeg_installer = FFmpegInstaller(self._settings_manager)
        self.ffmpeg_installer.finished.connect(self._on_ffmpeg_ready)
        self.ffmpeg_dialog = None
        # --------------------------------------------------------

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

        # ---- NOVO: verifica FFmpeg ao final da inicialização ----
        self._check_ffmpeg()

    # NOVO: métodos adicionados
    def _check_ffmpeg(self):
        """Verifica a disponibilidade do FFmpeg e oferece instalação se necessário."""
        if not self.ffmpeg_installer.is_available():
            reply = QMessageBox.question(
                self,
                "Componente necessário",
                "O FFmpeg não foi encontrado.\n"
                "Ele é necessário para conversões de vídeo/áudio.\n\n"
                "Deseja instalá-lo automaticamente?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self._start_ffmpeg_installation()

    def _start_ffmpeg_installation(self):
        """Abre uma diálogo de progresso e inicia o download em segundo plano."""
        # Pergunta onde instalar
        default_dir = str(Path.home() / "Documents" / "ffmpeg")
        selected_dir = QFileDialog.getExistingDirectory(
            self, "Selecione a pasta para instalar o FFmpeg", default_dir
        )

        if not selected_dir:
            return # Usuário cancelou a seleção da pasta

        target_path = Path(selected_dir)
        self.ffmpeg_dialog = QProgressDialog(
            "Instalando FFmpeg...", "Cancelar", 0, 100, self
        )
        self.ffmpeg_dialog.setWindowModality(Qt.WindowModal)
        self.ffmpeg_dialog.setAutoClose(False)

        self.ffmpeg_installer.progress.connect(self.ffmpeg_dialog.setValue)
        self.ffmpeg_installer.status_message.connect(self.ffmpeg_dialog.setLabelText)

        # O download é bloqueante, então usamos uma thread dedicada
        threading.Thread(
            target=self.ffmpeg_installer.install, 
            args=(target_path,), 
            daemon=True
        ).start()

    def _on_ffmpeg_ready(self, success, result):
        """Chamado quando a instalação termina (sucesso ou falha)."""
        if self.ffmpeg_dialog:
            self.ffmpeg_dialog.close()
            self.ffmpeg_dialog = None

        if success:
            # Comunica o caminho ao ProcessManager através do ThreadManager
            self._manager._get_process_manager().set_ffmpeg_location(result)
            QMessageBox.information(
                self,
                "Instalação Concluída",
                "O FFmpeg foi instalado com sucesso!\n"
                "Agora você já pode baixar vídeos em alta qualidade e converter para MP3."
            )
        else:
            QMessageBox.critical(
                self,
                "Erro na instalação",
                f"Não foi possível instalar o FFmpeg:\n{result}\n\n"
                "Você pode instalá-lo manualmente e reiniciar o aplicativo.",
            )

    # ------------------------------------------------------------

    def _on_open_folder_requested(self, task_id: int) -> None:
        """Abre o explorador de arquivos na pasta do download concluído."""
        task = self._manager.get_task(task_id)
        if task and task.file_path:
            file_path = Path(task.file_path).absolute()
            folder_path = file_path.parent
            
            if folder_path.exists():
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder_path)))
            else:
                QMessageBox.warning(self, "Erro", "A pasta de destino não foi encontrada.")
        else:
            QMessageBox.warning(self, "Erro", "Caminho do arquivo não disponível.")

    def _signal_connections(self):
        return (
            (self.view.input_bar.download_requested, self._slots.slot_download_requested),
            (self.view.queue_panel.cancel_requested, self._download_controller.confirm_cancel),
            (self.view.queue_panel.status_changed, self._on_task_status_changed),
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

    def _on_task_status_changed(self, task_id: int, status: str) -> None:
        """Intercepta mudanças de status para dar feedback adicional ao usuário."""
        if status == "completed":
            task = self._manager.get_task(task_id)
            # Usa o título do vídeo ou o ID como fallback
            name = task.title if task and task.title else f"Download #{task_id}"
            self.view.log_widget.log(f"✅ Download concluído com sucesso: {name}")
            # Opcional: Você poderia adicionar um som de notificação aqui

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