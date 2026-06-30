import os
import threading
from pathlib import Path
from PySide6.QtCore import QRectF, Qt, QUrl
from PySide6.QtWidgets import QMainWindow, QMessageBox, QProgressDialog, QFileDialog, QVBoxLayout, QWidget
from PySide6.QtGui import QDesktopServices, QPainterPath, QRegion
from PySide6.QtWidgets import QMainWindow, QMessageBox, QProgressDialog, QFileDialog

from core.app_info import APP_NAME
from core.settings_manager import SettingsManager
from core.thread_manager import ThreadManager
from core.ffmpeg_installer import FFmpegInstaller
from services import DesktopApiService

from ui.controllers import (
    DownloadController,
    HistoryController,
    SettingsController,
    ShutdownController,
)
from ui.slots import MainWindowSlots
from ui.utils.signals import connect_many, disconnect_many
from ui.views import MainView
from ui.widgets.title_bar import TitleBar


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
        self._api_service = DesktopApiService(fake_mode=False)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(960, 700)
        self.resize(1024, 750)

        self.view = MainView.build()
        self._title_bar = TitleBar(self)
        self._shell = self._build_shell()
        self.setCentralWidget(self._shell)

        # instalador do FFmpeg e diálogo de progresso ----
        self.ffmpeg_installer = FFmpegInstaller(self._settings_manager)
        self.ffmpeg_installer.finished.connect(self._on_ffmpeg_ready)
        self.ffmpeg_dialog = None

        self._download_controller = DownloadController(
            manager=self._manager,
            logger=self.view.log_widget,
            parent_widget=self,
        )
        self._history_controller = HistoryController(
            manager=self._manager,
            history_panel=self.view.history_panel,
            api_service=self._api_service,
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

        self._check_ffmpeg()

    
    def _build_shell(self) -> QWidget:
        shell = QWidget()
        shell.setObjectName("appShell")
        shell.setProperty("windowState", "normal")
        layout = QVBoxLayout(shell)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(0)
        layout.addWidget(self._title_bar)
        layout.addWidget(self.view.root, stretch=1)
        return shell

    def changeEvent(self, event):
        super().changeEvent(event)
        if not hasattr(self, "_shell"):
            return

        is_maximized = self.isMaximized() or self.isFullScreen()
        self._shell.setProperty("windowState", "maximized" if is_maximized else "normal")
        layout = self._shell.layout()
        if layout is not None:
            margin = 0 if is_maximized else 1
            layout.setContentsMargins(margin, margin, margin, margin)
        self._shell.style().unpolish(self._shell)
        self._shell.style().polish(self._shell)
        self._apply_window_shape()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_window_shape()

    def _apply_window_shape(self) -> None:
        if self.isMaximized() or self.isFullScreen():
            self.clearMask()
            return

        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()).adjusted(0, 0, -1, -1), 12, 12)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

    # métodos adicionados
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
            self._add_app_log(
                "ffmpeg_install_completed",
                status="completed",
                message="FFmpeg instalado com sucesso",
            )
            QMessageBox.information(
                self,
                "Instalação Concluída",
                "O FFmpeg foi instalado com sucesso!\n"
                "Agora você já pode baixar vídeos em alta qualidade e converter para MP3."
            )
        else:
            self._add_app_log(
                "ffmpeg_install_error",
                status="error",
                message="Erro ao instalar FFmpeg",
                error_message=result,
            )
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
            (self.view.queue_panel.task_status_changed, self._on_task_status_changed),
            (self.view.queue_panel.status_changed, self._slots.slot_status_changed),
            (self.view.queue_panel.error_reported, self._slots.slot_download_error_reported),
            (self.view.history_panel.clear_requested, self._history_controller.clear_history),
            (self.view.logs_panel.clear_requested, self._clear_app_logs),
            (self.view.settings_btn.clicked, self._settings_controller.open_settings),
            (self._settings_controller.download_path_changed, self._slots.slot_download_path_changed),
            (self._settings_controller.download_format_changed, self._slots.slot_download_format_changed),
            (self._settings_controller.download_quality_changed, self._slots.slot_download_quality_changed),
            (self._settings_controller.concurrent_downloads_changed, self._slots.slot_concurrent_downloads_changed),
            (self._settings_controller.theme_changed, self._slots.slot_apply_theme),
            (self._settings_controller.ytdlp_updated, self._on_ytdlp_updated),
            (self.view.tabs.currentChanged, self._slots.slot_tab_changed),
        )

    def _on_task_status_changed(self, task_id: int, status: str) -> None:
        """Intercepta mudanças de status para dar feedback adicional ao usuário."""
        task = self._manager.get_task(task_id)
        name = task.title if task and task.title else f"Download #{task_id}"

        if task is not None and self._api_service.get_download_by_local_task(task_id) is None:
            self._api_service.create_download(
                local_task_id=task_id,
                url=task.url,
                title=task.title,
                status=task.status,
                download_format=task.download_format,
                quality=task.quality,
                format_spec=task.format_spec,
                is_audio=task.audio,
            )

        if task is not None:
            self._api_service.update_download_by_local_task(
                task_id,
                title=task.title,
                status=task.status,
                file_path=task.file_path,
                error_message=task.error_msg,
                total_bytes=task.total_bytes,
                avg_speed_kbps=task.avg_speed_kbps,
                progress=task.progress,
                started_at=task.started_at,
                finished_at=task.finished_at,
                duration_seconds=task.duration_seconds,
            )

        if status == "running":
            self._add_app_log(
                "download_started",
                status="running",
                message=f"Download iniciado: {name}",
                download_id=task_id,
            )
        if status == "completed":
            self.view.log_widget.log(f"Download concluído com sucesso: {name}")
            self._add_app_log(
                "download_completed",
                status="completed",
                message=f"Download concluído: {name}",
                download_id=task_id,
            )
        elif status == "cancelled":
            self._add_app_log(
                "download_cancelled",
                status="cancelled",
                message=f"Download cancelado: {name}",
                download_id=task_id,
            )
        elif status == "error":
            self._add_app_log(
                "download_error",
                status="error",
                message=f"Erro no download: {name}",
                download_id=task_id,
                error_message=task.error_msg if task else "",
            )

    def _add_app_log(
        self,
        event_type: str,
        *,
        status: str = "",
        message: str = "",
        download_id: int | None = None,
        error_message: str = "",
    ) -> None:
        remote_download_id = download_id
        if download_id is not None:
            record = self._api_service.get_download_by_local_task(download_id)
            if record is not None:
                remote_download_id = record.id

        self._api_service.create_log(
            event_type,
            status=status,
            message=message,
            download_id=remote_download_id,
            error_message=error_message,
        )
        self._refresh_app_logs()

    def _refresh_app_logs(self) -> None:
        self.view.logs_panel.refresh(self._api_service.list_logs())

    def _clear_app_logs(self) -> None:
        self._api_service.clear_logs()
        self._refresh_app_logs()

    def _on_ytdlp_updated(self) -> None:
        self._add_app_log(
            "ytdlp_updated",
            status="completed",
            message="yt-dlp atualizado com sucesso",
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
