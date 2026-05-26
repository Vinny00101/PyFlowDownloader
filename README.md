<p align="center">
  <img src="assets/pyflow512.png" width="180" alt="PyFlowDownloader logo">
</p>

<h1 align="center">PyFlowDownloader</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PySide6-Qt-green?logo=qt&logoColor=white" alt="PySide6">
  <img src="https://img.shields.io/badge/yt--dlp-media-red" alt="yt-dlp">
  <img src="https://img.shields.io/badge/PyInstaller-build-purple" alt="PyInstaller">
</p>

PyFlowDownloader e um gerenciador de downloads desktop feito em Python. O sistema usa PySide6 para a interface grafica e yt-dlp para baixar videos ou audios, com suporte a fila de downloads, progresso em tempo real, cancelamento, historico e exportacao CSV.

## Requisitos Do Sistema

- Python 3.10 ou superior.
- Windows, Linux ou macOS com ambiente grafico disponivel.
- Conexao com a internet.
- ffmpeg instalado para downloads em MP3 e videos em alta qualidade que precisam juntar video e audio.
- Permissao de escrita na pasta de videos do usuario.

## Requisitos Antes De Usar

- Instale as dependencias Python com `pip install -r requirements.txt`.
- Mantenha o `yt-dlp` atualizado para reduzir erros com YouTube: `pip install -U yt-dlp`.
- Instale o `ffmpeg` quando for baixar MP3, `1080p`, `best` ou qualquer formato que use video e audio separados.
- No Windows, o sistema procura o `ffmpeg` automaticamente em `C:/ffmpeg/bin/ffmpeg.exe`.
- Se o `ffmpeg` estiver em outro lugar, adicione a pasta `bin` ao `PATH` ou configure uma das variaveis `FFMPEG_BINARY`, `FFMPEG_PATH` ou `FFMPEG_HOME`.

## Requisitos Funcionais Atuais

- Receber uma URL informada pelo usuario.
- Validar e normalizar URLs digitadas sem protocolo.
- Permitir escolha entre `mp4` e `mp3`.
- Permitir escolha de qualidade para video: `144p`, `360p`, `720p`, `1080p` ou `best`.
- Adicionar downloads em uma fila visual.
- Executar downloads em segundo plano sem travar a interface.
- Exibir progresso, velocidade e ETA do download.
- Permitir cancelamento de downloads ativos ou pendentes.
- Registrar mensagens no painel de logs.
- Exibir historico de tarefas finalizadas, canceladas ou com erro.
- Filtrar historico por titulo ou URL.
- Exportar historico concluido para CSV.
- Aplicar tema visual via QSS.
- Alternar tela cheia com `F11`.

## Bibliotecas Usadas

### Dependencias Externas

- `PySide6`: cria a interface grafica desktop. Usado em janelas, widgets, layouts, sinais, slots, timers, dialogs, tabelas e barras de progresso.
- `yt-dlp`: baixa videos e audios. Usado em `core/process_manager.py` via `yt_dlp.YoutubeDL`.
- `ffmpeg`: dependencia externa do sistema usada pelo `yt-dlp` para converter audio para MP3 e juntar video/audio em downloads de alta qualidade.

### Bibliotecas Python Padrao

- `sys`: usado no ponto de entrada para controlar argumentos e encerrar a aplicacao.
- `pathlib.Path`: usado para manipular caminhos de forma portavel.
- `threading`: usado para locks e eventos de cancelamento.
- `concurrent.futures.ThreadPoolExecutor`: executa downloads em threads separadas.
- `concurrent.futures.Future`: acompanha tarefas submetidas ao executor.
- `dataclasses.dataclass`: define a estrutura `DownloadTask`.
- `dataclasses.field`: cria `stop_event` por instancia de tarefa.
- `typing`: usado para `Protocol`, `Optional`, `Callable` e tipagens auxiliares.
- `datetime`: registra horarios de conclusao, cancelamento e logs.
- `csv`: exporta o historico para arquivo CSV.
- `os`: le variaveis de ambiente usadas para localizar o `ffmpeg`.
- `shutil`: verifica se `ffmpeg` esta disponivel no PATH.
- `urllib.parse.urlparse`: valida e normaliza URLs digitadas pelo usuario.

## Qualidade De Video E ffmpeg

- A opcao `best` usa `bestvideo+bestaudio/best` para tentar obter a melhor qualidade disponivel.
- As opcoes `144p`, `360p`, `720p` e `1080p` usam filtros de altura do yt-dlp, como `bestvideo[height<=1080]+bestaudio`.
- Quando o YouTube entrega video e audio separados, o `ffmpeg` e necessario para gerar um arquivo final unico.
- Quando encontrado, o caminho do `ffmpeg` e enviado ao yt-dlp pela opcao `ffmpeg_location`.

## Como Executar

```bash
pip install -r requirements.txt
python main.py
```

Para baixar MP3 ou videos em alta qualidade, instale o `ffmpeg`. O caminho recomendado no Windows e `C:/ffmpeg/bin/ffmpeg.exe`.

## Build Local

O projeto usa PyInstaller para gerar o executavel Windows.

```powershell
.\scripts\build.ps1
```

O pacote final sera criado em:

```text
releases/PyFlowDownloader-dev-windows.zip
```

Para informar uma versao manualmente:

```powershell
.\scripts\build.ps1 -Version "v0.1.0"
```

Se as dependencias ja estiverem instaladas:

```powershell
.\scripts\build.ps1 -Version "v0.1.0" -SkipInstall
```

## Pipeline De Release

O projeto possui uma pipeline em `.github/workflows/release.yml`.

Ela executa automaticamente quando uma tag no formato `vMAJOR.MINOR.PATCH` e enviada para o GitHub.

Fluxo da pipeline:

1. Baixa o codigo do repositorio.
2. Instala Python 3.12.
3. Instala as dependencias do `requirements.txt`.
4. Executa o build com `scripts/build.ps1`.
5. Compacta o executavel em `.zip`.
6. Cria uma GitHub Release.
7. Anexa o `.zip` da versao na Release.

## Como Criar Uma Nova Versao

O projeto segue essa estrutura de versão:

```text
vMAJOR.MINOR.PATCH
```

Exemplos:

```text
v0.1.0  primeira versao testavel
v0.2.0  nova funcionalidade
v0.2.1  correcao de bug
v1.0.0  versao estavel
```

Para criar uma release:

```bash
git tag v0.1.0
git push origin v0.1.0
```

Depois do push da tag, o GitHub Actions cria a Release automaticamente.

Antes de criar a tag, atualize o `CHANGELOG.md` com as mudancas da versao.

## Observacao Sobre ffmpeg Na Release

O `ffmpeg` nao e empacotado junto com o aplicativo nesta primeira estrutura de release.

Motivos:

- Mantem o build menor.
- Evita problemas de distribuicao/licenca.
- O sistema ja detecta `ffmpeg` no `PATH`, em variaveis de ambiente e em `C:/ffmpeg/bin/ffmpeg.exe`.

Para usar MP3 ou alta qualidade, instale o `ffmpeg` separadamente.
