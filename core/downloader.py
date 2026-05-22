"""
Funções auxiliares para download que integram ThreadManager + ProcessManager.

Cada função pode ser usada diretamente ou submetida ao ThreadManager.
"""

from pathlib import Path
from typing import Callable, Optional

from core.process_manager import ProcessManager


# Alerta de não uso — todo o módulo


def run_download(
    url: str,
    output_dir: str = "downloads",
    output_template: str = "%(title)s.%(ext)s",
    format_spec: str = "best",
    progress_hook: Optional[Callable] = None,
    stop_event: Optional[Callable[[], bool]] = None,
) -> Path:
    """Executa o download usando yt-dlp via ProcessManager."""
    if stop_event is not None:
        def wrapped_hook(d):
            if stop_event():
                raise Exception("Cancelado pelo usuário")
            if progress_hook:
                progress_hook(d)
        hook = wrapped_hook
    else:
        hook = progress_hook

    pm = ProcessManager(output_dir=output_dir)
    return pm.download(
        url=url,
        output_template=output_template,
        format_spec=format_spec,
        progress_hook=hook,
    )


def run_download_audio(
    url: str,
    output_dir: str = "downloads",
    output_template: str = "%(title)s.%(ext)s",
    format_spec: str = "bestaudio/best",
    progress_hook: Optional[Callable] = None,
    stop_event: Optional[Callable[[], bool]] = None,
) -> Path:
    """Executa download de áudio usando yt-dlp."""
    if stop_event is not None:
        def wrapped_hook(d):
            if stop_event():
                raise Exception("Cancelado pelo usuário")
            if progress_hook:
                progress_hook(d)
        hook = wrapped_hook
    else:
        hook = progress_hook

    pm = ProcessManager(output_dir=output_dir)
    return pm.download_audio(
        url=url,
        output_template=output_template,
        format_spec=format_spec,
        progress_hook=hook,
    )
