# theme.py
# ─────────────────────────────────────────────
# Estrutura base dos temas. Não contém cores
# hard-coded — tudo vem de theme_colors.THEMES.
# Para mudar uma cor, edite theme_colors.py.
# ─────────────────────────────────────────────

from .theme_colors import THEMES

# Placeholders usam a sintaxe {token} do str.format_map()
_BASE_THEME = """
QMainWindow, QWidget {{
    background-color: {bg_base};
    color: {text_primary};
    font-family: "Segoe UI", sans-serif;
    font-size: 13px;
}}

QMessageBox {{
    background-color: {bg_surface};
    color: {text_primary};
}}
QMessageBox QLabel {{
    background-color: transparent;
    color: {text_primary};
}}
QMessageBox QPushButton {{
    background-color: {secondary};
    color: {text_primary};
    border: 1px solid {border};
    border-radius: 10px;
    min-width: 72px;
    min-height: 32px;
    padding: 6px 14px;
}}
QMessageBox QPushButton:hover {{
    background-color: {secondary_hover};
}}
QMessageBox QPushButton:pressed {{
    background-color: {bg_elevated};
}}
QMessageBox QPushButton:disabled {{
    background-color: {secondary};
    color: {text_subtle};
    border-color: {border};
}}

QWidget#appShell {{
    background-color: {bg_base};
    border: 1px solid {window_border};
    border-radius: 12px;
}}
QWidget#appShell[windowState="maximized"] {{
    border: none;
    border-radius: 0px;
}}
QWidget#mainContent {{
    background-color: {bg_base};
    border-bottom-left-radius: 11px;
    border-bottom-right-radius: 11px;
}}
QWidget#appShell[windowState="maximized"] QWidget#mainContent {{
    border-bottom-left-radius: 0px;
    border-bottom-right-radius: 0px;
}}
QWidget#titleBar {{
    background-color: {bg_elevated};
    border-bottom: 1px solid {border};
    border-top-left-radius: 11px;
    border-top-right-radius: 11px;
}}
QWidget#appShell[windowState="maximized"] QWidget#titleBar {{
    border-top-left-radius: 0px;
    border-top-right-radius: 0px;
}}
QLabel#titleBarTitle {{
    color: {text_primary};
    font-size: 12px;
    font-weight: 500;
}}
QLabel#titleBarIcon {{
    background-color: transparent;
}}
QPushButton#windowControlBtn,
QPushButton#windowCloseBtn {{
    background-color: transparent;
    border: none;
    border-radius: 7px;
    padding: 0;
}}
QPushButton#windowControlBtn:hover {{
    background-color: {secondary_hover};
}}
QPushButton#windowControlBtn:pressed {{
    background-color: {secondary};
}}
QPushButton#windowCloseBtn:hover {{
    background-color: {danger};
}}
QPushButton#windowCloseBtn:pressed {{
    background-color: {danger_hover};
}}

QLineEdit, QComboBox, QTextEdit, QSpinBox {{
    background-color: {bg_surface};
    border: 1px solid {border};
    border-radius: 12px;
    padding: 9px 11px;
    color: {text_primary};
    selection-background-color: {selection};
}}
QLineEdit:focus, QComboBox:focus {{
    border-color: {accent};
    background-color: {bg_elevated};
}}
QLineEdit::placeholder {{ color: {text_subtle}; }}
QComboBox {{
    padding-right: 30px;
}}
QComboBox::drop-down {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 30px;
    border: none;
    background-color: transparent;
}}
QComboBox::down-arrow {{
    image: url(assets/chevron-down.svg);
    width: 12px;
    height: 12px;
    background-color: transparent;
}}
QComboBox QAbstractItemView {{
    background-color: {bg_surface};
    color: {text_primary};
    border: 1px solid {border};
    border-radius: 10px;
    selection-background-color: {selection};
    outline: none;
}}

QPushButton {{
    background-color: {accent};
    color: {on_accent};
    border: 1px solid {accent};
    border-radius: 12px;
    padding: 9px 18px;
    font-weight: 600;
}}
QPushButton:hover   {{ background-color: {accent_hover}; }}
QPushButton:pressed {{ background-color: {accent_press}; }}
QPushButton:disabled {{
    background-color: {secondary};
    color: {text_subtle};
}}

QPushButton#secondaryBtn {{
    background-color: {secondary};
    color: {text_primary};
    border: 1px solid {border};
}}
QPushButton#secondaryBtn:hover {{ background-color: {secondary_hover}; }}
QPushButton#secondaryBtn:pressed {{ background-color: {bg_surface}; }}

QPushButton#dangerBtn {{
    background-color: transparent;
    color: {danger};
    border: 1px solid {danger};
}}
QPushButton#dangerBtn:hover {{
    background-color: {danger};
    color: {on_danger};
}}
QPushButton#dangerBtn:pressed {{ background-color: {danger_hover}; }}

QPushButton#windowControlBtn,
QPushButton#windowCloseBtn {{
    background-color: transparent;
    color: {text_primary};
    border: none;
    border-radius: 7px;
    padding: 0;
}}
QPushButton#windowControlBtn:hover {{
    background-color: {secondary_hover};
}}
QPushButton#windowControlBtn:pressed {{
    background-color: {secondary};
}}
QPushButton#windowCloseBtn:hover {{
    background-color: {danger};
}}
QPushButton#windowCloseBtn:pressed {{
    background-color: {danger_hover};
}}

QProgressBar {{
    border: none;
    border-radius: 5px;
    background-color: {bg_surface};
    text-align: center;
    color: {text_primary};
    height: 10px;
}}
QProgressBar::chunk {{
    background-color: {success};
    border-radius: 5px;
}}

QListWidget, QTableWidget {{
    background-color: {bg_surface};
    border: 1px solid {border};
    border-radius: 16px;
    outline: none;
    gridline-color: {border};
}}
QListWidget::item, QTableWidget::item {{
    padding: 6px;
    border-bottom: 1px solid {bg_base};
}}
QListWidget::item:selected {{
    background-color: {selection};
}}
QTableWidget::item:selected {{
    background-color: {selection};
    color: {text_primary};
}}

QHeaderView::section {{
    background-color: {bg_elevated};
    color: {text_muted};
    padding: 9px;
    border: none;
    border-bottom: 1px solid {border};
}}
QFrame#tableFrame {{
    background-color: {bg_surface};
    border: 1px solid {border};
    border-radius: 16px;
}}
QTableWidget#historyTable {{
    background-color: transparent;
    border: none;
    border-radius: 15px;
}}
QTableWidget#historyTable QHeaderView::section {{
    background-color: transparent;
    color: {text_muted};
    border: none;
    border-bottom: 1px solid {border};
    padding: 10px 9px;
}}
QTableWidget#historyTable QHeaderView {{
    background-color: transparent;
}}
QTableWidget#historyTable QTableCornerButton::section {{
    background-color: transparent;
    border: none;
    border-bottom: 1px solid {border};
}}
QTableWidget#historyTable::item {{
    border-bottom: 1px solid {bg_surface};
}}

QTabWidget::pane {{
    border: none;
    background-color: transparent;
    top: -1px;
}}
QTabWidget QWidget {{
    background-color: transparent;
}}
QTabBar::tab {{
    background-color: transparent;
    color: {text_muted};
    padding: 10px 16px;
    margin-right: 6px;
    margin-bottom: 8px;
    border: 1px solid transparent;
    border-radius: 12px;
}}
QTabBar::tab:selected {{
    background-color: {bg_elevated};
    color: {text_primary};
    border: 1px solid {border};
}}
QTabBar::tab:hover {{
    color: {text_primary};
    background-color: {secondary};
}}

QLabel#titleLabel {{
    font-size: 24px;
    font-weight: 700;
    color: {text_primary};
}}
QLabel#subtitleLabel {{
    color: {text_subtle};
    font-size: 11px;
}}

QGroupBox {{
    border: 1px solid {border};
    border-radius: 16px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: {accent};
}}

QScrollBar:vertical {{
    background: {bg_base};
    width: 10px;
    border-radius: 5px;
}}
QScrollBar::handle:vertical {{
    background: {border};
    border-radius: 5px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{ background: {text_subtle}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QScrollArea {{
    background-color: transparent;
    border: 1px solid {border};
    border-radius: 18px;
}}
QScrollArea > QWidget > QWidget {{
    background-color: transparent;
}}

DownloadCard#downloadCard {{
    background-color: {bg_elevated};
    border: 1px solid {border};
    border-radius: 16px;
}}
QLabel#cardTitle {{
    color: {text_primary}; font-weight: 600; font-size: 13px;
}}
QLabel#cardStatus, QLabel#cardSpeed, QLabel#cardEta {{
    color: {text_subtle}; font-size: 11px;
}}
QLabel#cardStatus[state="error"] {{ color: {danger}; }}
QLabel#cardStatus[state="completed"] {{ color: {success}; }}
QLabel#cardStatus[state="muted"] {{ color: {text_subtle}; }}
QTextEdit#logPanel {{
    background-color: {bg_surface};
    color: {text_muted};
    border: 1px solid {border};
    border-radius: 16px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 11px;
}}
QLabel#statusBar {{
    color: {text_subtle}; font-size: 11px;
}}
QLabel#versionLabel {{
    color: {text_subtle}; font-size: 11px;
}}

QFrame#settingsHeader {{
    border: 1px solid {border};
    border-radius: 10px;
}}
QTreeWidget#settingsSidebar {{
    background-color: {bg_surface};
    border: 1px solid {border};
    border-radius: 12px;
    padding: 8px 6px;
    outline: none;
}}
QTreeWidget#settingsSidebar::item {{
    background-color: transparent;
    color: {text_muted};
    padding: 5px 8px;
    margin: 1px 0;
    border: none;
    border-left: 2px solid transparent;
    border-radius: 0px;
    outline: none;
}}
QTreeWidget#settingsSidebar::item:hover {{
    color: {text_primary};
    background-color: {secondary};
}}
QTreeWidget#settingsSidebar::item:selected {{
    background-color: transparent;
    color: {text_primary};
    border-left: 2px solid {accent};
}}
QTreeWidget#settingsSidebar::branch {{
    background-color: transparent;
    border: none;
    width: 0px;
}}
QTreeWidget#settingsSidebar::branch:has-children:closed,
QTreeWidget#settingsSidebar::branch:closed:has-children {{
    image: none;
}}
QTreeWidget#settingsSidebar::branch:has-children:open,
QTreeWidget#settingsSidebar::branch:open:has-children {{
    image: none;
}}
QTreeWidget#settingsSidebar::branch:!has-children {{
    image: none;
}}
QTreeWidget#settingsSidebar::branch:selected,
QTreeWidget#settingsSidebar::branch:hover,
QTreeWidget#settingsSidebar::branch:focus {{
    background-color: transparent;
    border: none;
    image: none;
}}
QFrame#settingsSection {{
    background-color: transparent;
    border: none;
}}
QLabel#settingsChevron {{
    background-color: transparent;
    border: none;
}}
QLabel#settingsSectionTitle {{
    background-color: transparent;
    color: {text_primary};
    font-weight: 700;
}}
QStackedWidget#settingsContent {{
    background-color: {bg_surface};
    border: 1px solid {border};
    border-radius: 10px;
}}
QFrame#settingsPage {{
    background-color: transparent;
}}
QFrame#settingsHeader QLabel, QFrame#settingsPage QLabel {{
    background-color: transparent;
}}
"""


def get_theme(name: str) -> str:
    """Retorna o stylesheet QSS para o tema solicitado.

    Args:
        name: "dark" ou "light" (default: "light" para nomes desconhecidos).
    """
    colors = THEMES.get(name, THEMES["light"])
    return _BASE_THEME.format_map(colors)

