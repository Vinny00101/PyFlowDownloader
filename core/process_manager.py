"""Integração com yt-dlp para obter informações e baixar mídias.

Este módulo concentra todo o contato direto com a biblioteca yt_dlp.
O restante do sistema não precisa conhecer os detalhes de configuração do
`YoutubeDL`; ele apenas chama os métodos de `ProcessManager`.
"""

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
    """Gerencia as operações de download feitas com `yt-dlp`.

    responsabilidades principais:
    - Baixar vídeo em MP4 ou outro formato escolhido.
    - Baixar áudio e converter para MP3 usando o pós-processador do yt-dlp.
    - Montar as opções usadas pela API `yt_dlp.YoutubeDL`.

    args:
        output_dir: Pasta onde os arquivos baixados serão salvos. Caso a pasta
            não exista, ela é criada automaticamente.
    """

    def __init__(self, output_dir: str = "downloads"):
        """Inicializa o gerenciador e garante que a pasta de saída exista.

        args:
            output_dir: Caminho da pasta onde os downloads serão salvos.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download(
        self,
        url: str,
        output_template: str = "%(title)s.%(ext)s",
        format_spec: str = "best",
        progress_hook: Optional[Callable] = None,
    ) -> Path:
        """Baixa uma mídia como vídeo/arquivo usando yt-dlp.

        args:
            url: Link da mídia que será baixada.
            output_template: Modelo de nome do arquivo final. O padrão %(title)s.%(ext)s usa o título e a extensão detectados pelo yt-dlp.
            format_spec: Especificação de formato do yt-dlp. Exemplos: best, best[height<=720]/best, worst[height<=144]/worst.
            progress_hook: Função opcional chamada pelo yt-dlp durante o download. O sistema usa esse hook para atualizar progresso, velocidade e ETA na interface.

        returns:
            Caminho esperado do arquivo baixado.
        """
        opts = self.get_dict_options(format_spec, output_template)

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
        """Baixa apenas o áudio e converte para MP3 por padrão.

        Este método usa os pós-processadores do yt-dlp. Por padrão, configura
        FFmpegExtractAudio, que depende do ffmpeg instalado no sistema.

        args:
            url: Link da mídia que terá o áudio baixado.
            output_template: Modelo de nome do arquivo temporário/final usado pelo yt-dlp.
            format_spec: Formato de áudio solicitado ao yt-dlp. O padrão bestaudio/best escolhe o melhor áudio disponível.
            postprocessors: Lista de pós-processadores do yt-dlp. Se None, usa conversão padrão para MP3 com qualidade 192 kbps.
            progress_hook: Função opcional chamada pelo yt-dlp durante o download para informar progresso.

        returns:
            Caminho esperado do arquivo de áudio convertido.
        """
        if postprocessors is None:
            postprocessors = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ]

        opts = self.get_dict_options(format_spec, output_template)
        opts["postprocessors"] = postprocessors

        if progress_hook is not None:
            opts["progress_hooks"] = [progress_hook]

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "unknown")
            codec = postprocessors[0].get("preferredcodec", "mp3")
            return self.output_dir / f"{title}.{codec}"


    def get_dict_options(
        self,
        format_spec: str,
        output_template: str = "%(title)s.%(ext)s"
    ) -> dict:
        """Monta o dicionário de opções enviado para `yt_dlp.YoutubeDL`.

        args:
            format_spec: Formato desejado para o download.
            postprocessors: Pós-processadores usados depois do download, 
            como conversão de áudio para MP3. Pode ser None quando não houver pós-processamento.
            output_template: Modelo de nome do arquivo de saída.

        returns:
            Dicionário de opções compatível com `yt_dlp.YoutubeDL`.
        """
        opts: dict = {
            "format": format_spec,
            "outtmpl": str(self.output_dir / output_template),
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
        }
        return opts
