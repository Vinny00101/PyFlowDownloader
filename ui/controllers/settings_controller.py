from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QWidget

from ui.widgets.settings_dialog import SettingsDialog



SETTINGS_SECTIONS = [
    ("Aparência", ["Tema"]),
    ("Downloads", ["Pasta padrão", "Format opadrão", "Qualidade padrão", "Downloads simultâneos"]),
    ("Ferramentas", ["Caminho do ffmpeg", "Testar ffmpeg", "Versão do yt-dlp", "Atualizar yt-dlp"]),
    ("YouTube", ["Cookies do navegador"]),
]

class SettingsController(QObject):
    """Abre a tela de configurações."""

    def __init__(self, parent_widget: QWidget) -> None:
        super().__init__(parent_widget)
        self._parent_widget = parent_widget

    @Slot()
    def open_settings(self) -> None:
        dialog = SettingsDialog(parent=self._parent_widget, sections=SETTINGS_SECTIONS)
        dialog.exec()
