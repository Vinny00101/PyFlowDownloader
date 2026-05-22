from PySide6.QtCore import Qt
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

    def __init__(self, task_id: int, title: str, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.task_id = task_id

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

    def update_progress(self, value: float, status: str, speed: str, eta: str) -> None:
        self.progress_bar.setValue(int(value))

        status_map = {
            "pending": "Aguardando...",
            "running": "Baixando",
            "completed": "Concluído",
            "error": "Erro",
            "cancelled": "Cancelado",
            "paused": "Pausado",
        }
        status_text = status_map.get(status, status)
        self.status_label.setText(status_text)

        if status == "error":
            self.status_label.setStyleSheet("color: #f7768e; font-size: 11px;")
        elif status == "completed":
            self.status_label.setStyleSheet("color: #9ece6a; font-size: 11px;")
            self.cancel_btn.setVisible(False)
        elif status == "cancelled":
            self.status_label.setStyleSheet("color: #565f89; font-size: 11px;")
            self.cancel_btn.setVisible(False)
        else:
            self.status_label.setStyleSheet("color: #565f89; font-size: 11px;")

        if status == "running":
            self.speed_label.setText(speed)
            self.eta_label.setText(eta if eta else "")
        else:
            self.speed_label.setText("")
            self.eta_label.setText("")
