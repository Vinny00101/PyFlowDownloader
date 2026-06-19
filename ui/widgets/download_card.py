from PySide6.QtCore import Qt
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class DownloadCard(QFrame):
    """Card exibindo o progresso de um único download na fila."""

    open_folder_requested = Signal(int)

    def __init__(self, task_id: int, title: str, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.task_id = task_id
        self._last_progress = -1
        self._last_status = ""
        self._last_speed = None
        self._last_eta = None

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("downloadCard")

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(6)

        top_row = QHBoxLayout()
        self.title_label = QLabel(title or "Carregando título...")
        self.title_label.setObjectName("cardTitle")
        self.title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        top_row.addWidget(self.title_label)

        self.open_folder_btn = QPushButton("Abrir Pasta")
        self.open_folder_btn.setFixedSize(90, 26)
        self.open_folder_btn.setObjectName("secondaryBtn")
        self.open_folder_btn.setVisible(False)
        top_row.addWidget(self.open_folder_btn)

        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.setFixedSize(80, 26)
        self.cancel_btn.setObjectName("dangerBtn")
        top_row.addWidget(self.cancel_btn)
        root.addLayout(top_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        root.addWidget(self.progress_bar)

        bottom_row = QHBoxLayout()
        self.status_label = QLabel("Aguardando...")
        self.status_label.setObjectName("cardStatus")
        bottom_row.addWidget(self.status_label)

        bottom_row.addStretch()

        self.speed_label = QLabel("")
        self.speed_label.setObjectName("cardSpeed")
        self.speed_label.setMinimumWidth(80)
        self.speed_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        bottom_row.addWidget(self.speed_label)

        self.eta_label = QLabel("")
        self.eta_label.setObjectName("cardEta")
        self.eta_label.setMinimumWidth(60)
        self.eta_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        bottom_row.addWidget(self.eta_label)

        root.addLayout(bottom_row)

        self.open_folder_btn.clicked.connect(lambda: self.open_folder_requested.emit(self.task_id))

    def update_progress(self, value: float, status: str, speed: str, eta: str) -> None:
        progress = max(0, min(100, int(value)))
        if progress != self._last_progress:
            self.progress_bar.setValue(progress)
            self._last_progress = progress

        if status != self._last_status:
            self._apply_status(status)
            self._last_status = status

        speed_text = speed if status == "running" else ""
        eta_text = eta if status == "running" and eta else ""

        if speed_text != self._last_speed:
            self.speed_label.setText(speed_text)
            self._last_speed = speed_text
        if eta_text != self._last_eta:
            self.eta_label.setText(eta_text)
            self._last_eta = eta_text

    def _apply_status(self, status: str) -> None:
        status_map = {
            "pending": "Aguardando...",
            "running": "Baixando",
            "completed": "Concluído",
            "error": "Erro",
            "cancelled": "Cancelado",
            "paused": "Pausado",
        }
        self.status_label.setText(status_map.get(status, status))

        if status == "error":
            self.status_label.setStyleSheet("color: #f7768e;")
        elif status == "completed":
            self.status_label.setStyleSheet("color: #9ece6a;")
            self.cancel_btn.setVisible(False)
            self.open_folder_btn.setVisible(True)
        elif status == "cancelled":
            self.status_label.setStyleSheet("color: #565f89;")
            self.cancel_btn.setVisible(False)
            self.open_folder_btn.setVisible(False)
        else:
            self.status_label.setStyleSheet("color: #565f89;")
            self.cancel_btn.setVisible(True)
