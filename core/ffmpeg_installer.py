"""Instalação assistida do FFmpeg no Windows/macOS."""

import os
import sys
import zipfile
from pathlib import Path
from urllib.request import urlretrieve

from PySide6.QtCore import QObject, Signal

from .ffmpeg_finder import find_ffmpeg   # seu módulo existente com a função find_ffmpeg

# URLs oficiais de builds estáticas
FFMPEG_WIN_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
FFMPEG_MAC_URL = "https://evermeet.cx/ffmpeg/getrelease/zip"


class FFmpegInstaller(QObject):
    """Detecta, baixa e extrai o FFmpeg, emitindo progresso para a UI."""

    progress = Signal(int)              # 0 – 100
    status_message = Signal(str)
    finished = Signal(bool, str)        # sucesso, caminho_ou_erro

    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings = settings_manager
        self._cached_path = self.settings.get("tools.ffmpeg_path")

    def is_available(self) -> bool:
        """Verifica se o FFmpeg já está acessível (caminho salvo ou sistema)."""
        if self._cached_path and os.path.isfile(self._cached_path):
            return True
        if find_ffmpeg() is not None:
            return True
        return False

    def get_ffmpeg_path(self) -> str:
        """Retorna o caminho do binário a ser utilizado."""
        if self._cached_path and os.path.isfile(self._cached_path):
            return self._cached_path
        found = find_ffmpeg()
        return found if found else "ffmpeg"   # fallback (pode falhar)

    def install(self, dest_dir: Path | None = None) -> None:
        """Inicia o download e a extração. Deve ser chamada em uma thread separada."""
        self.progress.emit(0)
        self.status_message.emit("Baixando FFmpeg...")

        if dest_dir is None:
            dest_dir = self._get_install_dir()
        dest_dir.mkdir(parents=True, exist_ok=True)

        url = FFMPEG_WIN_URL if sys.platform == "win32" else FFMPEG_MAC_URL

        try:
            zip_path = dest_dir / "ffmpeg.zip"
            urlretrieve(url, zip_path, reporthook=self._report_progress)

            self.status_message.emit("Extraindo FFmpeg...")
            self.progress.emit(0)  # Reinicia o progresso para a fase de extração
            self._extract(zip_path, dest_dir)
            os.remove(zip_path)

            bin_path = self._find_binary(dest_dir)
            self._cached_path = str(bin_path)
            self.settings.set("tools.ffmpeg_path", self._cached_path)
            self.settings.save()

            self.finished.emit(True, self._cached_path)
        except Exception as e:
            self.finished.emit(False, str(e))

    def _report_progress(self, count, block_size, total_size):
        if total_size > 0:
            percent = min(int(count * block_size * 100 / total_size), 100)
            self.progress.emit(percent)

    def _extract(self, zip_path, dest_dir):
        with zipfile.ZipFile(zip_path, "r") as zf:
            members = zf.infolist()
            total = len(members)
            for i, member in enumerate(members, 1):
                zf.extract(member, dest_dir)
                # Emite o progresso baseado na quantidade de arquivos extraídos
                self.progress.emit(int(i / total * 100))

    def _find_binary(self, directory):
        if sys.platform == "win32":
            candidates = list(Path(directory).rglob("ffmpeg.exe"))
            if candidates:
                return candidates[0]
            raise FileNotFoundError("ffmpeg.exe não encontrado após extração")
        else:
            ffmpeg = directory / "ffmpeg"
            if ffmpeg.exists():
                ffmpeg.chmod(0o755)
                return ffmpeg
            raise FileNotFoundError("Binário ffmpeg não encontrado")

    def _get_install_dir(self) -> Path:
        base = os.getenv("APPDATA") or os.path.expanduser("~/.pyflowdownloader")
        return Path(base) / "PyFlowDownloader" / "ffmpeg"