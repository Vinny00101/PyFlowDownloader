import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from core.settings_manager import SettingsManager
from core.thread_manager import ThreadManager
from ui.main_window import MainWindow


def _asset_path(relative_path: str) -> Path:
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_path / relative_path


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(_asset_path("assets/pyflow256x256.ico"))))

    settings_manager = SettingsManager()
    max_workers = settings_manager.get("downloads.concurrent_downloads", 3)
    path = settings_manager.get("downloads.default_path")
    manager = ThreadManager(max_workers=max_workers, output_dir=str(path))

    window = MainWindow(manager=manager, settings_manager=settings_manager)
    window.setWindowIcon(QIcon(str(_asset_path("assets/pyflow256x256.ico"))))
    window.show()

    exit_code = app.exec()
    manager.shutdown(wait=False)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
