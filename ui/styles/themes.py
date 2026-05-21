DARK_THEME = """
QMainWindow, QWidget {
    background-color: #1a1b26;
    color: #c0caf5;
    font-family: "Segoe UI", sans-serif;
    font-size: 13px;
}
QLineEdit, QComboBox, QTextEdit, QSpinBox {
    background-color: #24283b;
    border: 1px solid #414868;
    border-radius: 6px;
    padding: 8px;
    color: #c0caf5;
}
QLineEdit:focus, QComboBox:focus {
    border-color: #7aa2f7;
}
QPushButton {
    background-color: #7aa2f7;
    color: #1a1b26;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}
QPushButton:hover { background-color: #89b4fa; }
QPushButton:pressed { background-color: #5a7fd4; }
QPushButton:disabled { background-color: #414868; color: #565f89; }
QPushButton#secondaryBtn {
    background-color: #414868;
    color: #c0caf5;
}
QPushButton#secondaryBtn:hover { background-color: #565f89; }
QPushButton#dangerBtn {
    background-color: #f7768e;
    color: #1a1b26;
}
QPushButton#dangerBtn:hover { background-color: #ff9eaf; }
QProgressBar {
    border: none;
    border-radius: 4px;
    background-color: #24283b;
    text-align: center;
    color: #c0caf5;
    height: 8px;
}
QProgressBar::chunk {
    background-color: #9ece6a;
    border-radius: 4px;
}
QListWidget, QTableWidget {
    background-color: #24283b;
    border: 1px solid #414868;
    border-radius: 8px;
    outline: none;
}
QListWidget::item, QTableWidget::item {
    padding: 4px;
    border-bottom: 1px solid #1a1b26;
}
QListWidget::item:selected {
    background-color: #364a82;
}
QHeaderView::section {
    background-color: #1f2335;
    color: #7aa2f7;
    padding: 8px;
    border: none;
}
QTabWidget::pane {
    border: 1px solid #414868;
    border-radius: 8px;
    background-color: #24283b;
}
QTabBar::tab {
    background-color: #1f2335;
    color: #a9b1d6;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}
QTabBar::tab:selected {
    background-color: #7aa2f7;
    color: #1a1b26;
}
QLabel#titleLabel {
    font-size: 22px;
    font-weight: 700;
    color: #7aa2f7;
}
QLabel#subtitleLabel { color: #565f89; font-size: 11px; }
QGroupBox {
    border: 1px solid #414868;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #7aa2f7;
}
QScrollBar:vertical {
    background: #1a1b26;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #414868;
    border-radius: 4px;
    min-height: 20px;
}
"""

LIGHT_THEME = """
QMainWindow, QWidget {
    background-color: #f5f7fb;
    color: #1e293b;
    font-family: "Segoe UI", sans-serif;
    font-size: 13px;
}
QLineEdit, QComboBox, QTextEdit, QSpinBox {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px;
    color: #1e293b;
}
QLineEdit:focus, QComboBox:focus { border-color: #3b82f6; }
QPushButton {
    background-color: #3b82f6;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}
QPushButton:hover { background-color: #2563eb; }
QPushButton#secondaryBtn {
    background-color: #e2e8f0;
    color: #1e293b;
}
QPushButton#dangerBtn {
    background-color: #ef4444;
    color: #ffffff;
}
QProgressBar {
    border: none;
    border-radius: 4px;
    background-color: #e2e8f0;
    height: 8px;
}
QProgressBar::chunk {
    background-color: #22c55e;
    border-radius: 4px;
}
QListWidget, QTableWidget {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
}
QLabel#titleLabel {
    font-size: 22px;
    font-weight: 700;
    color: #3b82f6;
}
QTabBar::tab:selected {
    background-color: #3b82f6;
    color: #ffffff;
}
"""


def get_theme(name: str) -> str:
    return DARK_THEME if name == "dark" else LIGHT_THEME
