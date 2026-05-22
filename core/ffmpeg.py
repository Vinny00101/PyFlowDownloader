import os
import shutil
from pathlib import Path


def find_ffmpeg() -> str | None:
    """Procura o executável do ffmpeg no sistema.

    A busca cobre os casos mais comuns no Windows: ffmpeg no PATH, caminho
    definido por variável de ambiente e instalações extraídas em pastas padrão.
    """
    path_from_system = shutil.which("ffmpeg")
    if path_from_system:
        return path_from_system

    for env_name in ("FFMPEG_BINARY", "FFMPEG_PATH", "FFMPEG_HOME"):
        path = _resolve_candidate(os.environ.get(env_name))
        if path:
            return str(path)

    for path in _common_windows_paths():
        if path.exists():
            return str(path)

    return None


def _resolve_candidate(value: str | None) -> Path | None:
    if not value:
        return None

    path = Path(value).expanduser()
    if path.is_file():
        return path

    if path.is_dir():
        for candidate in (path / "ffmpeg.exe", path / "bin" / "ffmpeg.exe"):
            if candidate.exists():
                return candidate

    return None


def _common_windows_paths() -> list[Path]:
    home = Path.home()
    fixed_paths = [
        Path("C:/ffmpeg/bin/ffmpeg.exe")
    ]

    extracted_paths: list[Path] = []
    for parent in (home / "Downloads", home / "Documents"):
        if parent.exists():
            extracted_paths.extend(parent.glob("ffmpeg*/bin/ffmpeg.exe"))

    return fixed_paths + extracted_paths
