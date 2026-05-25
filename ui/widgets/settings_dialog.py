from collections.abc import Sequence

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QLabel,
    QStackedWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QWidget,
)

from ui.styles.theme_colors import THEMES

SettingsSections = Sequence[tuple[str, Sequence[str]]]


class SettingsDialog(QDialog):
    """Janela modal de configurações com sidebar e páginas internas."""

    update_ytdlp_requested = Signal()

    def __init__(
        self,
        parent: QWidget | None = None,
        sections: SettingsSections = (),
    ) -> None:
        super().__init__(parent)
        self._sections = sections
        self.setWindowTitle("Configurações")
        self.setModal(True)
        self.setFixedSize(QSize(800, 600))
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        root.addWidget(self._build_header())

        body = QHBoxLayout()
        body.setSpacing(16)

        self._sidebar = self._build_sidebar()
        self._pages = QStackedWidget()
        self._pages.setObjectName("settingsContent")

        body.addWidget(self._sidebar, stretch=0)
        body.addWidget(self._pages, stretch=1)
        root.addLayout(body, stretch=1)

        self._populate_pages()
        self._sidebar.currentItemChanged.connect(self._on_sidebar_changed)

        first = self._sidebar.topLevelItem(0)
        if first is not None:
            self._sidebar.setCurrentItem(first)

    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setObjectName("settingsHeader")

        layout = QVBoxLayout(header)
        layout.setContentsMargins(18, 14, 18, 14)

        title = QLabel("Configurações")
        title.setObjectName("titleLabel")
        subtitle = QLabel("Organize aqui as preferências da aplicação.")
        subtitle.setObjectName("subtitleLabel")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        return header

    def _build_sidebar(self) -> QTreeWidget:
        sidebar = QTreeWidget()
        sidebar.setObjectName("settingsSidebar")
        sidebar.setHeaderHidden(True)
        sidebar.setIndentation(12)
        sidebar.setFixedWidth(220)
        sidebar.setItemsExpandable(True)
        sidebar.setExpandsOnDoubleClick(False)
        return sidebar

    def _populate_pages(self) -> None:
        for section, links in self._sections:
            section_item = self._add_sidebar_item(section, is_section=True)
            self._add_page(section_item, section, None)
            section_item.setExpanded(True)
            for link in links:
                item = self._add_sidebar_item(link, parent=section_item)
                self._add_page(item, section, link)

    def _add_sidebar_item(
        self,
        title: str,
        is_section: bool = False,
        parent: QTreeWidgetItem | None = None,
    ) -> QTreeWidgetItem:
        item = QTreeWidgetItem([title])
        item.setSizeHint(0, QSize(0, 34 if is_section else 28))
        if is_section:
            font = QFont()
            font.setBold(True)
            item.setFont(0, font)
        if parent is None:
            self._sidebar.addTopLevelItem(item)
        else:
            parent.addChild(item)
        if is_section:
            self._sidebar.setItemWidget(item, 0, _SectionLabel(title))
        return item

    def _add_page(
        self,
        item: QTreeWidgetItem,
        section: str,
        title: str | None,
    ) -> int:
        page = QFrame()
        page.setObjectName("settingsPage")

        layout = QVBoxLayout(page)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(10)

        if title == "Tema":
            self._build_theme_page(layout)
        elif title == "Atualizar yt-dlp":
            self._build_update_ytdlp_page(layout)
        elif title and "yt-dlp" in title:
            self._build_ytdlp_version_page(layout)
        else:
            page_title = QLabel(title or section)
            page_title.setObjectName("cardTitle")
            page_subtitle = QLabel(
                "Área reservada para configurar esta opção."
                if title
                else "Selecione uma opção no menu lateral para configurar."
            )
            page_subtitle.setObjectName("subtitleLabel")
            page_subtitle.setWordWrap(True)

            layout.addWidget(page_title)
            layout.addWidget(page_subtitle)
            layout.addStretch()

        index = self._pages.addWidget(page)
        item.setData(0, Qt.UserRole, index)
        return index

    def _build_theme_page(self, layout: QVBoxLayout) -> None:
        label = QLabel("Selecione o tema:")
        label.setObjectName("cardTitle")
        layout.addWidget(label)

        self._theme_combo = QComboBox()
        self._theme_combo.addItems(list(THEMES.keys()))

        current_theme = "dark"
        parent = self.parentWidget()
        if parent is not None and hasattr(parent, "_settings"):
            current_theme = parent._settings.get("theme", "dark")
        self._theme_combo.setCurrentText(current_theme)
        layout.addWidget(self._theme_combo)

        apply_btn = QPushButton("Aplicar tema")
        apply_btn.setObjectName("secondaryBtn")
        apply_btn.clicked.connect(self._on_apply_theme)
        layout.addWidget(apply_btn)
        layout.addStretch()

    def _build_ytdlp_version_page(self, layout: QVBoxLayout) -> None:
        title = QLabel("Versão do yt-dlp")
        title.setObjectName("cardTitle")
        layout.addWidget(title)

        info = QLabel(f"Versão instalada: {self._get_ytdlp_version()}")
        info.setObjectName("subtitleLabel")
        layout.addWidget(info)
        layout.addStretch()

    def _build_update_ytdlp_page(self, layout: QVBoxLayout) -> None:
        title = QLabel("Atualizar yt-dlp")
        title.setObjectName("cardTitle")
        layout.addWidget(title)

        description = QLabel(
            "Use esta opção quando o YouTube pedir login, cookies ou mostrar "
            "erros de confirmação de acesso."
        )
        description.setObjectName("subtitleLabel")
        description.setWordWrap(True)
        layout.addWidget(description)

        update_btn = QPushButton("Atualizar yt-dlp")
        update_btn.setObjectName("secondaryBtn")
        update_btn.clicked.connect(self.update_ytdlp_requested.emit)
        layout.addWidget(update_btn)
        layout.addStretch()

    @staticmethod
    def _get_ytdlp_version() -> str:
        try:
            from yt_dlp.version import __version__
        except Exception:
            return "não instalado"
        return __version__

    def _on_apply_theme(self) -> None:
        theme_name = self._theme_combo.currentText()
        parent = self.parentWidget()
        if parent is not None and hasattr(parent, "apply_theme"):
            parent.apply_theme(theme_name)

    def _on_sidebar_changed(
        self,
        current: QTreeWidgetItem | None,
        _previous: QTreeWidgetItem | None,
    ) -> None:
        if current is None:
            return
        if current.parent() is not None:
            parent = current.parent()
            self._sidebar.blockSignals(True)
            self._sidebar.setCurrentItem(parent)
            self._sidebar.blockSignals(False)

        index = current.data(0, Qt.UserRole)
        if isinstance(index, int):
            self._pages.setCurrentIndex(index)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._center_on_parent()

    def _center_on_parent(self) -> None:
        parent = self.parentWidget()
        if parent is None:
            screen = self.screen().availableGeometry()
            frame = self.frameGeometry()
            frame.moveCenter(screen.center())
            self.move(frame.topLeft())
            return

        parent_frame = parent.frameGeometry()
        frame = self.frameGeometry()
        frame.moveCenter(parent_frame.center())
        self.move(frame.topLeft())


class _SectionLabel(QFrame):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.setObjectName("settingsSection")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 0, 4, 0)

        label = QLabel(text)
        label.setObjectName("settingsSectionTitle")
        layout.addWidget(label)
