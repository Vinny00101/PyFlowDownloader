from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


TEAM_MEMBERS = [
    "Vinicius Andrade de Sousa",
    "Allyson Michel",
    "Kleber Moura",
    "Rian",
]


class TeamDevPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QScrollArea.NoFrame)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(18)
        content_layout.setAlignment(Qt.AlignTop)

        content_layout.addWidget(self._build_team_card())
        content_layout.addWidget(self._build_about_card())
        content_layout.addStretch()

        scroll.setWidget(content)
        root.addWidget(scroll)

    def _build_team_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("settingsPage")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("Equipe de Desenvolvimento")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        members = QHBoxLayout()
        members.setSpacing(10)
        members.setAlignment(Qt.AlignLeft)
        for name in TEAM_MEMBERS:
            label = QLabel(name)
            label.setObjectName("subtitleLabel")
            label.setAlignment(Qt.AlignCenter)
            members.addWidget(label)

        layout.addLayout(members)
        return card

    def _build_about_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("settingsPage")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("Sobre o Projeto")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        about = QLabel(
            "PyFlowDownloader e um gerenciador de downloads desktop feito em Python. "
            "O sistema usa PySide6 para a interface grafica e yt-dlp para baixar "
            "videos ou audios, com suporte a fila de downloads, progresso em tempo "
            "real, cancelamento, historico e exportacao CSV."
        )
        about.setObjectName("subtitleLabel")
        about.setWordWrap(True)
        about.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(about)

        return card
