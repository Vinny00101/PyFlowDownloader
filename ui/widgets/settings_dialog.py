from collections.abc import Sequence

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QStackedWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.settings_manager import SettingsManager
from ui.styles.theme_colors import THEMES
from ui.utils.constants import FORMAT, QUALITY
from ui.utils.widgets import card_title, secondary_button, subtitle

SettingsSections = Sequence[tuple[str, Sequence[str]]]


class SettingsDialog(QDialog):
    """Janela modal de configurações com sidebar e páginas internas."""

    download_format_changed = Signal(str)
    download_quality_changed = Signal(str)
    concurrent_downloads_changed = Signal(int)
    download_path_changed = Signal(str)
    theme_changed = Signal(str)
    update_ytdlp_requested = Signal()

    def __init__(
        self,
        parent: QWidget | None = None,
        sections: SettingsSections = (),
        settings_manager: SettingsManager | None = None,
    ) -> None:
        super().__init__(parent)
        self._sections = sections
        self._settings_manager = settings_manager
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

        layout.addWidget(title)
        layout.addWidget(subtitle("Organize aqui as preferências da aplicação."))
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
        elif title == "Pasta padrão":
            self._build_download_path_page(layout)
        elif title == "Formato padrão":
            self._build_default_format(layout)
        elif title == "Qualidade padrão":
            self._build_default_quality(layout)
        elif title == "Downloads simultâneos":
            self._build_concurrent_downloads(layout)
        elif title == "Atualizar yt-dlp":
            self._build_update_ytdlp_page(layout)
        elif title and "yt-dlp" in title:
            self._build_ytdlp_version_page(layout)
        else:
            self._build_placeholder_page(layout, title or section, title is not None)

        index = self._pages.addWidget(page)
        item.setData(0, Qt.UserRole, index)
        return index

    def _build_placeholder_page(
        self,
        layout: QVBoxLayout,
        title: str,
        is_option: bool,
    ) -> None:
        message = (
            "Área reservada para configurar esta opção."
            if is_option
            else "Selecione uma opção no menu lateral para configurar."
        )
        layout.addWidget(card_title(title))
        layout.addWidget(subtitle(message))
        layout.addStretch()

    def _build_theme_page(self, layout: QVBoxLayout) -> None:
        layout.addWidget(card_title("Selecione o tema:"))

        self._theme_combo = QComboBox()
        self._theme_combo.addItems(list(THEMES.keys()))
        self._theme_combo.setCurrentText(self._get_setting("appearance.theme", "dark"))
        layout.addWidget(self._theme_combo)

        apply_btn = secondary_button("Aplicar tema")
        apply_btn.clicked.connect(self._on_apply_theme)
        layout.addWidget(apply_btn)
        layout.addStretch()

    def _build_download_path_page(self, layout: QVBoxLayout) -> None:
        layout.addWidget(card_title("Pasta padrão"))
        layout.addWidget(subtitle("Escolha onde os próximos vídeos serão salvos."))

        self._download_path_label = subtitle(
            self._get_setting("downloads.default_path", "")
        )
        layout.addWidget(self._download_path_label)

        choose_btn = secondary_button("Escolher pasta")
        choose_btn.clicked.connect(self._on_choose_download_path)
        layout.addWidget(choose_btn)
        layout.addStretch()

    def _build_ytdlp_version_page(self, layout: QVBoxLayout) -> None:
        layout.addWidget(card_title("Versão do yt-dlp"))
        layout.addWidget(subtitle(f"Versão instalada: {self._get_ytdlp_version()}"))
        layout.addStretch()

    def _build_update_ytdlp_page(self, layout: QVBoxLayout) -> None:
        layout.addWidget(card_title("Atualizar yt-dlp"))
        layout.addWidget(
            subtitle(
                "Use esta opção quando o YouTube pedir login, cookies ou mostrar "
                "erros de confirmação de acesso."
            )
        )

        update_btn = secondary_button("Atualizar yt-dlp")
        update_btn.clicked.connect(self.update_ytdlp_requested.emit)
        layout.addWidget(update_btn)
        layout.addStretch()

    def _build_default_format(self, layout: QVBoxLayout) -> None:
        layout.addWidget(card_title("Selecione o formato padrão:"))

        self._format_combo = QComboBox()
        self._format_combo.addItems(FORMAT)
        self._format_combo.setCurrentText(
            self._get_setting("downloads.default_format", "mp4")
        )
        layout.addWidget(self._format_combo)

        apply_btn = secondary_button("Aplicar formato padrão")
        apply_btn.clicked.connect(self._on_apply_format)
        layout.addWidget(apply_btn)
        layout.addStretch()

    def _build_default_quality(self, layout: QVBoxLayout) -> None:
        layout.addWidget(card_title("Selecione a qualidade de vídeo padrão:"))

        self._quality_combo = QComboBox()
        self._quality_combo.addItems(QUALITY)
        self._quality_combo.setCurrentText(
            self._get_setting("downloads.default_quality", "720p")
        )
        layout.addWidget(self._quality_combo)

        apply_btn = secondary_button("Aplicar a qualidade de vídeo padrão")
        apply_btn.clicked.connect(self._on_apply_quality)
        layout.addWidget(apply_btn)
        layout.addStretch()

    def _build_concurrent_downloads(self, layout: QVBoxLayout) -> None:
        layout.addWidget(card_title("Downloads simultâneos:"))
        layout.addWidget(subtitle("Defina quantos downloads podem rodar ao mesmo tempo."))

        self._concurrent_downloads_spin = QSpinBox()
        self._concurrent_downloads_spin.setRange(1, 32)
        self._concurrent_downloads_spin.setValue(
            int(self._get_setting("downloads.concurrent_downloads", 3))
        )
        layout.addWidget(self._concurrent_downloads_spin)

        apply_btn = secondary_button("Aplicar downloads simultâneos")
        apply_btn.clicked.connect(self._on_apply_concurrent_downloads)
        layout.addWidget(apply_btn)
        layout.addStretch()

    @staticmethod
    def _get_ytdlp_version() -> str:
        try:
            from yt_dlp.version import __version__
        except Exception:
            return "não instalado"
        return __version__

    def _get_setting(self, key_path: str, default):
        if self._settings_manager is None:
            return default
        return self._settings_manager.get(key_path, default)

    def _on_apply_format(self) -> None:
        self.download_format_changed.emit(self._format_combo.currentText())

    def _on_apply_theme(self) -> None:
        self.theme_changed.emit(self._theme_combo.currentText())

    def _on_apply_quality(self) -> None:
        self.download_quality_changed.emit(self._quality_combo.currentText())

    def _on_apply_concurrent_downloads(self) -> None:
        self.concurrent_downloads_changed.emit(self._concurrent_downloads_spin.value())

    def _on_choose_download_path(self) -> None:
        current_path = self._get_setting("downloads.default_path", "")
        selected_path = QFileDialog.getExistingDirectory(
            self,
            "Escolher pasta de downloads",
            current_path,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )
        if not selected_path:
            return

        self._download_path_label.setText(selected_path)
        self.download_path_changed.emit(selected_path)

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
