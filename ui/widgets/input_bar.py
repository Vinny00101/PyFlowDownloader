import shutil
from urllib.parse import urlparse

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QWidget,
)

class InputBar(QWidget):
    """Barra com campo de URL, seletores de formato/qualidade e botao Adicionar.

    Signals:
        download_requested(url, format_spec, is_audio): Emitido quando o
            usuario confirma um novo download.
    """

    download_requested = Signal(str, str, bool)  # url, format_spec, is_audio

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Cole a URL do YouTube aqui...")
        layout.addWidget(self.url_input, stretch=1)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["mp4", "mp3"])
        self.format_combo.setFixedWidth(80)
        layout.addWidget(self.format_combo)

        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["144p", "360p", "720p", "1080p", "best"])
        self.quality_combo.setFixedWidth(90)
        layout.addWidget(self.quality_combo)

        self.add_btn = QPushButton("Adicionar")
        layout.addWidget(self.add_btn)

        self.add_btn.clicked.connect(self._on_confirm)
        self.url_input.returnPressed.connect(self._on_confirm)

    def _on_confirm(self) -> None:
        url = self.url_input.text().strip()
        if not url:
            return

        url = self._normalize_url(url)
        if not url:
            QMessageBox.warning(self, "URL inválida", "Cole uma URL válida.")
            return

        fmt = self.format_combo.currentText()
        quality = self.quality_combo.currentText()
        format_spec = self._build_format_spec(fmt, quality)
        is_audio = fmt == "mp3"

        if is_audio and not self._ffmpeg_available():
            QMessageBox.warning(
                self,
                "ffmpeg não encontrado",
                "Para converter para MP3 é necessário instalar o ffmpeg "
                "e adicioná-lo ao PATH do sistema.\n\n"
                "Baixe em: https://ffmpeg.org/download.html",
            )
            return

        self.url_input.clear()
        self.download_requested.emit(url, format_spec, is_audio)

    @staticmethod
    def _normalize_url(url: str) -> str | None:
        parsed = urlparse(url)
        if parsed.scheme and parsed.netloc:
            return url
        if "." in url and not parsed.scheme:
            return "https://" + url
        return None

    @staticmethod
    def _build_format_spec(fmt: str, quality: str) -> str:
        if fmt == "mp3":
            return "bestaudio/best"
        if quality == "best":
            return "best"
        height = quality.replace("p", "")
        prefix = "worst" if height == "144" else "best"
        return f"{prefix}[height<={height}]/{prefix}"

    @staticmethod
    def _ffmpeg_available() -> bool:
        return shutil.which("ffmpeg") is not None
