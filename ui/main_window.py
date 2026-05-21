from pathlib import Path
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

# Importação do sistema de temas
from ui.styles.themes import get_theme

class MainWindow(QMainWindow):
    def __init__(
        self,
        settings=None,
        settings_path: Path = None,
        history=None,
        signals=None,
        manager=None,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._settings_path = settings_path
        self._history = history
        self._signals = signals
        self._manager = manager
        self._row_widgets = {}

        self.setWindowTitle("PyFlowDownloader")
        self.setMinimumSize(960, 700)
        self.resize(1024, 750)

        self._build_ui()
        self._apply_theme()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(16)
        root.setContentsMargins(20, 20, 20, 20)

        # Header Section
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

        self.settings_btn = QPushButton("Configurações")
        self.settings_btn.setObjectName("secondaryBtn")
        header.addWidget(self.settings_btn)
        root.addLayout(header)

        # URL Input Section
        url_row = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Cole a URL do YouTube aqui...")
        url_row.addWidget(self.url_input, stretch=1)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["mp4", "mp3"])
        self.format_combo.setFixedWidth(80)
        url_row.addWidget(self.format_combo)

        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["144p", "360p", "720p", "1080p", "best"])
        self.quality_combo.setFixedWidth(90)
        url_row.addWidget(self.quality_combo)

        self.add_btn = QPushButton("Adicionar")
        url_row.addWidget(self.add_btn)
        root.addLayout(url_row)

        # Main Content Section (Tabs)
        self.tabs = QTabWidget()

        # Tab: Fila
        queue_tab = QWidget()
        queue_layout = QVBoxLayout(queue_tab)
        self.queue_scroll = QScrollArea()
        self.queue_scroll.setWidgetResizable(True)
        self.queue_container = QWidget()
        self.queue_layout = QVBoxLayout(self.queue_container)
        self.queue_layout.addStretch()
        self.queue_scroll.setWidget(self.queue_container)
        queue_layout.addWidget(self.queue_scroll)
        self.tabs.addTab(queue_tab, "Fila de Downloads")

        # Tab: Histórico
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        hist_btn_row = QHBoxLayout()
        self.export_btn = QPushButton("Exportar CSV")
        self.export_btn.setObjectName("secondaryBtn")
        self.clear_hist_btn = QPushButton("Limpar histórico")
        self.clear_hist_btn.setObjectName("dangerBtn")
        hist_btn_row.addWidget(self.export_btn)
        hist_btn_row.addWidget(self.clear_hist_btn)
        hist_btn_row.addStretch()
        history_layout.addLayout(hist_btn_row)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Título", "URL", "Data", "Status", "Arquivo"])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        history_layout.addWidget(self.history_table)
        self.tabs.addTab(history_tab, "Histórico")

        root.addWidget(self.tabs, stretch=1)

        # Logs & Status
        log_label = QLabel("Logs")
        log_label.setStyleSheet("font-weight: 600; color: #7aa2f7;")
        root.addWidget(log_label)
        
        self.log_panel = QWidget() # Placeholder para o LogPanel customizado
        self.log_panel.setMinimumHeight(120)
        root.addWidget(self.log_panel)

        self.status_bar_label = QLabel("Pronto")
        self.status_bar_label.setStyleSheet("color: #565f89; font-size: 11px;")
        root.addWidget(self.status_bar_label)

    def _apply_theme(self) -> None:
        theme_name = self._settings.theme if self._settings else "dark"
        self.setStyleSheet(get_theme(theme_name))

    def toggle_fullscreen(self):
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
    