import os
import shutil
from pathlib import Path


def find_ffmpeg() -> str | None:
    """Procura o executável do ffmpeg no sistema.

    A busca cobre os casos mais comuns no Windows: ffmpeg no PATH, caminho
    definido por variável de ambiente e instalações extraídas em pastas padrão
    (incluindo a pasta de instalação automática do PyFlowDownloader).
    """
    path_from_system = shutil.which("ffmpeg")
    if path_from_system:
        return path_from_system

    for env_name in ("FFMPEG_BINARY", "FFMPEG_PATH", "FFMPEG_HOME"):
        path = _resolve_candidate(os.environ.get(env_name))
        if path:
            return str(path)

    # Procura em diretórios comuns onde o FFmpeg pode ser instalado ou extraído
    for base_dir in _common_windows_dirs():
        path = _resolve_candidate(str(base_dir))
        if path is not None:
            return str(path)
    return None


def _resolve_candidate(value: str | None) -> Path | None:
    if not value:
        return None

    path = Path(value).expanduser()
    if path.is_file():
        return path

    if path.is_dir():
        # Verifica caminhos comuns dentro do diretório base
        for candidate_subpath in ("ffmpeg.exe", "bin/ffmpeg.exe"):
            full_candidate = path / candidate_subpath
            if full_candidate.is_file():
                return full_candidate
        
        # Se não encontrou nos subcaminhos comuns, faz uma busca recursiva
        candidates = list(path.rglob("ffmpeg.exe"))
        if candidates:
            return candidates[0] # Retorna o primeiro encontrado

    return None


def _common_windows_dirs() -> list[Path]:
    """Retorna uma lista de diretórios comuns onde o FFmpeg pode ser encontrado."""
    home = Path.home()
    appdata = os.getenv("APPDATA")

    potential_dirs = [
        Path("C:/ffmpeg"), # Instalação manual comum
    ]

    # Adiciona o diretório de instalação automática do PyFlowDownloader
    if appdata:
        app_ffmpeg_install_dir = Path(appdata) / "PyFlowDownloader" / "ffmpeg"
        potential_dirs.append(app_ffmpeg_install_dir)

    # Adiciona diretórios onde o usuário pode ter extraído o FFmpeg (ex: Downloads, Documentos)
    for parent in (home / "Downloads", home / "Documents"): # Considerar apenas diretórios que começam com "ffmpeg"
        if parent.exists(): # para evitar rglob em pastas muito grandes
            for ffmpeg_dir in parent.glob("ffmpeg*"):
                if ffmpeg_dir.is_dir():
                    potential_dirs.append(ffmpeg_dir)

    return potential_dirs
