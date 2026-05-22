from datetime import datetime

from PySide6.QtWidgets import QTextEdit, QVBoxLayout, QWidget


class LogWidget(QWidget):
    """Painel de logs com metodo ``log()`` publico."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setMaximumHeight(120)
        self.text_edit.setObjectName("logPanel")
        layout.addWidget(self.text_edit)

    def log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.text_edit.append(f"[{timestamp}] {message}")
