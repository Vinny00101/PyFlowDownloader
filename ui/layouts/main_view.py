from dataclasses import dataclass

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ui.widgets import InputBar, LogWidget
from ui.widgets.panels import HistoryPanel, QueuePanel


@dataclass(slots=True)
class MainView:
    """Composicao visual da janela principal."""

    root: QWidget
    input_bar: InputBar
    queue_panel: QueuePanel
    history_panel: HistoryPanel
    log_widget: LogWidget
    tabs: QTabWidget
    status_bar_label: QLabel
    history_tab_idx: int
    settings_btn: QPushButton

    @classmethod
    def build(cls) -> "MainView":
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        header, settings_btn = _build_header()
        layout.addLayout(header)

        input_bar = InputBar()
        layout.addWidget(input_bar)

        tabs = QTabWidget()
        queue_panel = QueuePanel()
        tabs.addTab(queue_panel, "Fila de Downloads")

        history_panel = HistoryPanel()
        tabs.addTab(history_panel, "Histórico")
        history_tab_idx = tabs.count() - 1
        layout.addWidget(tabs, stretch=1)

        log_label = QLabel("Logs")
        log_label.setStyleSheet("font-weight: 600; color: #7aa2f7;")
        layout.addWidget(log_label)

        log_widget = LogWidget()
        layout.addWidget(log_widget)

        status_bar_label = QLabel("Pronto")
        status_bar_label.setObjectName("statusBar")
        layout.addWidget(status_bar_label)

        return cls(
            root=root,
            input_bar=input_bar,
            queue_panel=queue_panel,
            history_panel=history_panel,
            log_widget=log_widget,
            tabs=tabs,
            status_bar_label=status_bar_label,
            history_tab_idx=history_tab_idx,
            settings_btn=settings_btn,
        )


def _build_header() -> tuple[QHBoxLayout, QPushButton]:
    header = QHBoxLayout()
    title_box = QVBoxLayout()

    title = QLabel("PyFlowDownloader")
    title.setObjectName("titleLabel")
    subtitle = QLabel("Downloads simultâneos · Fila · Histórico")
    subtitle.setObjectName("subtitleLabel")

    title_box.addWidget(title)
    title_box.addWidget(subtitle)
    header.addLayout(title_box)
    header.addStretch()

    settings_btn = QPushButton("Configurações")
    settings_btn.setObjectName("secondaryBtn")
    # Alerta de não uso: settings_btn ainda não possui fluxo de configuração.
    header.addWidget(settings_btn)

    return header, settings_btn
