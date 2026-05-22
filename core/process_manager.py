from pathlib import Path
from typing import Callable, Optional

try:
    import yt_dlp
except ImportError:
    raise ImportError(
        "yt-dlp não está instalado.\n\n"
        "Para instalar, execute no terminal:\n"
        "  pip install yt-dlp\n\n"
        "Depois reinicie o aplicativo."
    )


class ProcessManager:
    """Encapsula operações do yt-dlp: extrair info, listar formatos, baixar."""

    def __init__(self, output_dir: str = "downloads"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_info(self, url: str) -> dict:
        opts: dict = {"quiet": True, "no_warnings": True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)

    def get_title(self, url: str) -> str:
        # Alerta de não uso
        return self.get_info(url).get("title", "unknown")

    def get_formats(self, url: str) -> list[dict]:
        # Alerta de não uso
        info = self.get_info(url)
        return info.get("formats", [])

    def download(
        self,
        url: str,
        output_template: str = "%(title)s.%(ext)s",
        format_spec: str = "best",
        progress_hook: Optional[Callable] = None,
    ) -> Path:
        opts: dict = {
            "format": format_spec,
            "outtmpl": str(self.output_dir / output_template),
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
        }
        if progress_hook is not None:
            opts["progress_hooks"] = [progress_hook]

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "unknown")
            ext = info.get("ext", "mp4")
            return self.output_dir / f"{title}.{ext}"

    def download_audio(
        self,
        url: str,
        output_template: str = "%(title)s.%(ext)s",
        format_spec: str = "bestaudio/best",
        postprocessors: Optional[list] = None,
        progress_hook: Optional[Callable] = None,
    ) -> Path:
        if postprocessors is None:
            postprocessors = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ]

        opts: dict = {
            "format": format_spec,
            "outtmpl": str(self.output_dir / output_template),
            "postprocessors": postprocessors,
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
        }
        if progress_hook is not None:
            opts["progress_hooks"] = [progress_hook]

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "unknown")
            codec = postprocessors[0].get("preferredcodec", "mp3")
            return self.output_dir / f"{title}.{codec}"
