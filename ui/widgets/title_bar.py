import sys
from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

from core.app_info import APP_ICON_PATH, APP_NAME


def _asset_path(relative_path: str) -> str:
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    return str(base_path / relative_path)


class TitleBar(QWidget):
    """Barra de titulo customizada para janela sem moldura."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("titleBar")
        self.setFixedHeight(34)
        self._drag_pos = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 8, 0)
        layout.setSpacing(8)

        icon = QLabel()
        icon.setObjectName("titleBarIcon")
        icon.setPixmap(QIcon(_asset_path(APP_ICON_PATH)).pixmap(16, 16))
        layout.addWidget(icon)

        title = QLabel(APP_NAME)
        title.setObjectName("titleBarTitle")
        layout.addWidget(title)
        layout.addStretch()

        self.minimize_btn = self._window_button("windowControlBtn", "assets/window-minimize.svg")
        self.maximize_btn = self._window_button("windowControlBtn", "assets/window-maximize.svg")
        self.close_btn = self._window_button("windowCloseBtn", "assets/window-close.svg")

        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.maximize_btn)
        layout.addWidget(self.close_btn)

        self.minimize_btn.clicked.connect(self._minimize_window)
        self.maximize_btn.clicked.connect(self._toggle_maximized)
        self.close_btn.clicked.connect(self._close_window)

    @staticmethod
    def _window_button(object_name: str, icon_path: str) -> QPushButton:
        button = QPushButton()
        button.setObjectName(object_name)
        button.setIcon(QIcon(_asset_path(icon_path)))
        button.setIconSize(QSize(12, 12))
        button.setFixedSize(42, 28)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        return button

    def _window(self):
        return self.window()

    def _minimize_window(self) -> None:
        self._window().showMinimized()

    def _toggle_maximized(self) -> None:
        window = self._window()
        if window.isMaximized():
            window.showNormal()
        else:
            window.showMaximized()
        self._sync_maximize_icon()

    def _close_window(self) -> None:
        self._window().close()

    def _sync_maximize_icon(self) -> None:
        icon = "assets/window-restore.svg" if self._window().isMaximized() else "assets/window-maximize.svg"
        self.maximize_btn.setIcon(QIcon(_asset_path(icon)))

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._toggle_maximized()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton and self._drag_pos is not None:
            window = self._window()
            if window.isMaximized():
                return
            delta = event.globalPosition().toPoint() - self._drag_pos
            window.move(window.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_pos = None
        super().mouseReleaseEvent(event)
