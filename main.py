import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from core.thread_manager import ThreadManager
from ui.main_window import MainWindow


def _asset_path(relative_path: str) -> Path:
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_path / relative_path


def _videos_dir() -> Path:
    home = Path.home()
    for name in ("Videos", "Vídeos", "My Videos", "Meus Vídeos"):
        p = home / name
        if p.exists():
            return p
    return home / "Videos"


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(_asset_path("assets/pyflow256x256.ico"))))

    output_dir = _videos_dir() / "PyFlowDownloader"
    output_dir.mkdir(exist_ok=True)

    manager = ThreadManager(max_workers=3, output_dir=str(output_dir))

    window = MainWindow(manager=manager)
    window.setWindowIcon(QIcon(str(_asset_path("assets/pyflow256x256.ico"))))
    window.show()

    exit_code = app.exec()
    manager.shutdown(wait=False)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
