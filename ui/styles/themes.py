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

QLineEdit, QComboBox, QTextEdit, QSpinBox {{
    background-color: {bg_surface};
    border: 1px solid {border};
    border-radius: 6px;
    padding: 8px;
    color: {text_primary};
}}
QLineEdit:focus, QComboBox:focus {{
    border-color: {accent};
}}

QPushButton {{
    background-color: {accent};
    color: {on_accent};
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
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
}}
QPushButton#secondaryBtn:hover {{ background-color: {secondary_hover}; }}

QPushButton#dangerBtn {{
    background-color: {danger};
    color: {on_danger};
}}
QPushButton#dangerBtn:hover {{ background-color: {danger_hover}; }}

QProgressBar {{
    border: none;
    border-radius: 4px;
    background-color: {bg_surface};
    text-align: center;
    color: {text_primary};
    height: 8px;
}}
QProgressBar::chunk {{
    background-color: {success};
    border-radius: 4px;
}}

QListWidget, QTableWidget {{
    background-color: {bg_surface};
    border: 1px solid {border};
    border-radius: 8px;
    outline: none;
}}
QListWidget::item, QTableWidget::item {{
    padding: 4px;
    border-bottom: 1px solid {bg_base};
}}
QListWidget::item:selected {{
    background-color: {selection};
}}

QHeaderView::section {{
    background-color: {bg_elevated};
    color: {accent};
    padding: 8px;
    border: none;
}}

QTabWidget::pane {{
    border: 1px solid {border};
    border-radius: 8px;
    background-color: {bg_surface};
}}
QTabBar::tab {{
    background-color: {bg_elevated};
    color: {text_muted};
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}}
QTabBar::tab:selected {{
    background-color: {accent};
    color: {on_accent};
}}

QLabel#titleLabel {{
    font-size: 22px;
    font-weight: 700;
    color: {accent};
}}
QLabel#subtitleLabel {{
    color: {text_subtle};
    font-size: 11px;
}}

QGroupBox {{
    border: 1px solid {border};
    border-radius: 8px;
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
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {border};
    border-radius: 4px;
    min-height: 20px;
}}

DownloadCard#downloadCard {{
    background-color: #1e2030;
    border: 1px solid #313244;
    border-radius: 8px;
}}
QLabel#cardTitle {{
    color: #c0caf5; font-weight: 600; font-size: 13px;
}}
QLabel#cardStatus, QLabel#cardSpeed, QLabel#cardEta {{
    color: #565f89; font-size: 11px;
}}
QTextEdit#logPanel {{
    background-color: #1a1b26;
    color: #565f89;
    border: 1px solid #313244;
    border-radius: 4px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 11px;
}}
QLabel#statusBar {{
    color: #565f89; font-size: 11px;
}}
"""


def get_theme(name: str) -> str:
    """Retorna o stylesheet QSS para o tema solicitado.

    Args:
        name: "dark" ou "light" (default: "light" para nomes desconhecidos).
    """
    colors = THEMES.get(name, THEMES["light"])
    return _BASE_THEME.format_map(colors)

