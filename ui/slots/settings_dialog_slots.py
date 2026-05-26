from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from core.settings_manager import SettingsManager


class SettingsDialogSlots(QObject):
    """Slots do diálogo de configurações."""

    download_format_changed = Signal(str)
    download_quality_changed = Signal(str)
    concurrent_downloads_changed = Signal(int)
    download_path_changed = Signal(str)
    theme_changed = Signal(str)

    def __init__(self, settings_manager: SettingsManager, parent=None) -> None:
        super().__init__(parent)
        self._settings_manager = settings_manager

    @Slot(str)
    def slot_download_format_changed(self, download_format: str) -> None:
        self._save_setting("downloads.default_format", download_format)
        self.download_format_changed.emit(download_format)

    @Slot(str)
    def slot_download_quality_changed(self, quality: str) -> None:
        self._save_setting("downloads.default_quality", quality)
        self.download_quality_changed.emit(quality)

    @Slot(int)
    def slot_concurrent_downloads_changed(self, max_workers: int) -> None:
        self._save_setting("downloads.concurrent_downloads", max_workers)
        self.concurrent_downloads_changed.emit(max_workers)

    @Slot(str)
    def slot_download_path_changed(self, path: str) -> None:
        self._save_setting("downloads.default_path", path)
        self.download_path_changed.emit(path)

    @Slot(str)
    def slot_theme_changed(self, theme_name: str) -> None:
        self._save_setting("appearance.theme", theme_name)
        self.theme_changed.emit(theme_name)

    def _save_setting(self, key_path: str, value) -> None:
        self._settings_manager.set(key_path, value)
        self._settings_manager.save()
