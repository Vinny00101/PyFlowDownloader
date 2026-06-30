from dataclasses import dataclass

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from core.app_info import APP_DESCRIPTION, APP_NAME, APP_VERSION
from ui.widgets import InputBar, LogWidget
from ui.widgets.panels import HistoryPanel, LogsPanel, QueuePanel, TeamDevPanel

@dataclass(slots=True)
class MainView:
    """Composição visual da janela principal."""

    root: QWidget
    input_bar: InputBar
    queue_panel: QueuePanel
    history_panel: HistoryPanel
    logs_panel: LogsPanel
    log_widget: LogWidget
    tabs: QTabWidget
    status_bar_label: QLabel
    version_label: QLabel
    history_tab_idx: int
    logs_tab_idx: int
    settings_btn: QPushButton

    @classmethod
    def build(cls) -> "MainView":
        root = QWidget()
        root.setObjectName("mainContent")
        layout = QVBoxLayout(root)
        layout.setSpacing(18)
        layout.setContentsMargins(22, 18, 22, 18)

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
        logs_panel = LogsPanel()
        tabs.addTab(logs_panel, "Logs")
        logs_tab_idx = tabs.count() - 1
        team_dev = TeamDevPanel()
        tabs.addTab(team_dev, "Equipe desenvolvimento")

        layout.addWidget(tabs, stretch=1)

        log_label = QLabel("Logs")
        log_label.setObjectName("settingsSectionTitle")
        layout.addWidget(log_label)

        log_widget = LogWidget()
        layout.addWidget(log_widget)

        status_bar_label = QLabel("Pronto")
        status_bar_label.setObjectName("statusBar")

        version_label = QLabel(f"v{APP_VERSION}")
        version_label.setObjectName("versionLabel")

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 0, 0, 0)
        footer.addWidget(status_bar_label)
        footer.addStretch()
        footer.addWidget(version_label)
        layout.addLayout(footer)

        return cls(
            root=root,
            input_bar=input_bar,
            queue_panel=queue_panel,
            history_panel=history_panel,
            logs_panel=logs_panel,
            log_widget=log_widget,
            tabs=tabs,
            status_bar_label=status_bar_label,
            version_label=version_label,
            history_tab_idx=history_tab_idx,
            logs_tab_idx=logs_tab_idx,
            settings_btn=settings_btn,
        )


def _build_header() -> tuple[QHBoxLayout, QPushButton]:
    header = QHBoxLayout()
    header.setSpacing(12)
    title_box = QVBoxLayout()
    title_box.setSpacing(2)
    title = QLabel(APP_NAME)
    title.setObjectName("titleLabel")
    subtitle = QLabel(APP_DESCRIPTION)
    subtitle.setObjectName("subtitleLabel")

    title_box.addWidget(title)
    title_box.addWidget(subtitle)
    header.addLayout(title_box)
    header.addStretch()

    settings_btn = QPushButton("Configurações")
    settings_btn.setObjectName("secondaryBtn")

    header.addWidget(settings_btn)
    return header, settings_btn
