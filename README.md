# Download Manager — Planejamento Arquitetural

Este documento descreve a arquitetura completa do projeto, a responsabilidade de cada tecnologia envolvida e o cronograma de desenvolvimento dividido em fases. O objetivo é servir como referência técnica durante toda a construção do sistema.

---

## Visao Geral do Sistema

O projeto consiste em um gerenciador de downloads desktop construido com Python e PySide6. Ele precisa ser capaz de:

- Baixar arquivos diretamente por link (HTTP/HTTPS), como arquivos ZIP, PDF, executaveis, entre outros.
- Baixar videos e streams de plataformas como YouTube, via integracao com a ferramenta `yt-dlp`.
- Retomar downloads interrompidos, salvando o estado em disco mesmo que o programa seja fechado no meio de um download.
- Executar multiplos downloads ao mesmo tempo sem travar a interface grafica.
- Exportar o historico de downloads concluidos para um arquivo CSV.

---

## Arquitetura dos Componentes

Cada tecnologia ou modulo do projeto tem uma responsabilidade especifica. A separacao clara de responsabilidades e o que permite que o sistema escale sem virar uma bola de neve de complexidade.

---

### 1. Arquivos em Python e Serialização com JSON

**Onde entra no projeto:** Gerenciamento de estado e persistencia de dados entre sessoes.

**Por que e necessario:**

Quando o usuario inicia um download de 2 GB e fecha o programa no meio do processo, esse progresso nao pode ser perdido. O sistema precisa de uma forma de gravar o estado atual de cada tarefa em disco e recarregar esse estado quando o programa for aberto novamente.

**Como funciona na pratica:**

O projeto mantera um arquivo `downloads.json` na pasta de dados do usuario. Esse arquivo e lido na inicializacao do programa para restaurar a lista de downloads anteriores na interface. A cada mudanca de estado (download iniciado, pausado, retomado, concluido ou com erro), o arquivo e reescrito com o novo estado.

Cada entrada no JSON representa uma tarefa de download com a seguinte estrutura:

```json
{
  "id": 1,
  "url": "https://exemplo.com/arquivo.zip",
  "caminho_destino": "/home/usuario/Downloads/arquivo.zip",
  "status": "pausado",
  "bytes_baixados": 450000,
  "total_bytes": 900000,
  "data_inicio": "2025-06-01T14:32:00",
  "velocidade_media_kbps": 1200
}
```

**Manipulacao de arquivos binarios:**

Quando uma thread estiver baixando um arquivo, ela usara `open("arquivo.zip.part", "ab")` para escrever os blocos de bytes no disco em modo binario (`ab` = append binary). O sufixo `.part` indica que o arquivo ainda nao foi completado. Ao terminar, o arquivo e renomeado para o nome final sem o sufixo.

**Modulos Python envolvidos:** `json`, `os`, `pathlib`, `datetime`

---

### 2. Serialização de Dados com CSV

**Onde entra no projeto:** Exportacao do historico de downloads concluidos.

**Por que e necessario:**

Gerenciadores de download profissionais oferecem a opcao de exportar um relatorio do que foi baixado. Isso e util para o usuario controlar seu consumo de banda, verificar quais arquivos foram baixados em determinado periodo ou simplesmente manter um registro organizado.

**Como funciona na pratica:**

Ao clicar em "Exportar Historico", o sistema percorre todos os downloads com status `concluido` no `downloads.json` e gera um arquivo `historico.csv` com as colunas:

```
Data de Inicio | Nome do Arquivo | URL de Origem | Tamanho (MB) | Velocidade Media (KB/s) | Caminho de Destino
```

O formato CSV foi escolhido porque pode ser aberto diretamente no Excel, LibreOffice Calc ou qualquer editor de planilhas sem configuracao adicional.

**Modulos Python envolvidos:** `csv`

---

### 3. PySide6 e Multithreading com QThreadPool

**Onde entra no projeto:** Interface grafica principal e motor de downloads diretos (HTTP/HTTPS).

**Por que e necessario:**

A interface grafica roda inteiramente na thread principal (Main Thread). Se um download for executado diretamente nessa thread, a janela congela completamente ate o download terminar. O usuario nao consegue clicar em nada, mover a janela ou interagir com o programa. O sistema operacional eventualmente exibe a mensagem "O aplicativo nao esta respondendo".

A solucao e executar cada download em uma thread separada, gerenciada pelo `QThreadPool`.

**Como funciona na pratica:**

Sera criada uma classe `DownloadWorker` que herda de `QRunnable`. Essa classe encapsula toda a logica de requisicao HTTP e escrita em disco. Ela nao interage diretamente com a interface — em vez disso, emite sinais (`QSignals`) com os dados de progresso, e a interface (na Main Thread) recebe esses sinais e atualiza os componentes visuais com seguranca.

O fluxo completo para um link direto:

1. Usuario cola uma URL no campo de texto e clica em "Baixar".
2. A interface cria uma instancia de `DownloadWorker` com os parametros do download.
3. A instancia e enviada para `QThreadPool.globalInstance()`, que decide quantas threads rodar em paralelo de acordo com o hardware.
4. O worker faz a requisicao HTTP com `requests.get(url, stream=True)` e itera sobre os chunks de resposta (blocos de 1024 ou 8192 bytes).
5. Para cada chunk recebido, o worker calcula a porcentagem de progresso e emite um sinal com o valor.
6. A interface recebe o sinal e atualiza a `QProgressBar` correspondente ao download.

**Componentes PySide6 envolvidos:**

- `QMainWindow`: janela principal do aplicativo.
- `QLineEdit`: campo de texto para colar a URL.
- `QPushButton`: botoes de acao (Baixar, Pausar, Cancelar, Exportar Historico).
- `QTreeWidget` ou `QTableWidget`: lista de downloads ativos e concluidos com colunas de nome, progresso, velocidade e status.
- `QProgressBar`: barra de progresso individual por download.
- `QRunnable`: classe base para o worker de download.
- `QThreadPool`: gerenciador de threads que executa os workers.
- `QObject` com `Signal`: classe auxiliar que carrega os sinais de progresso, pois `QRunnable` nao pode emitir sinais diretamente.
- `QMutex`: lock para proteger a gravacao no arquivo JSON contra condicoes de corrida.

---

### 4. Execucao de Processos Externos com QProcess

**Onde entra no projeto:** Downloads de videos e streams (YouTube e similares) e pos-processamento de midia.

**Por que e necessario:**

Baixar videos de plataformas de streaming envolve decodificar manifestos de protocolo como HLS (`.m3u8`) ou DASH, autenticacao de cookies, selecao de qualidade de video e audio, e em muitos casos o merge de streams separados de video e audio em um unico arquivo. Reimplementar tudo isso em Python seria um trabalho enorme e fragil.

A alternativa e delegar esse trabalho para o `yt-dlp`, uma ferramenta de linha de comando especializada nesse tipo de download, mantida ativamente pela comunidade e compativel com centenas de plataformas.

**Como funciona na pratica:**

Quando o usuario cola uma URL, o sistema verifica se ela contem padroes como `youtube.com`, `youtu.be` ou outros dominios suportados pelo `yt-dlp`. Se sim, o fluxo e redirecionado do `DownloadWorker` para um `QProcess`.

O `QProcess` executa o seguinte comando no terminal do sistema operacional:

```
yt-dlp --newline --progress "URL_DO_VIDEO" -o "/caminho/de/saida/%(title)s.%(ext)s"
```

A flag `--newline` faz com que cada atualizacao de progresso seja impressa em uma linha separada, o que facilita a leitura pelo codigo Python. A flag `--progress` garante que a saida de progresso seja exibida mesmo quando a saida padrao nao e um terminal interativo.

O `QProcess` roda de forma assincrona — ele nao bloqueia a interface. O sinal `readyReadStandardOutput` e conectado a uma funcao que le cada nova linha de saida do processo. Essa funcao procura por linhas no formato:

```
[download]  45.2% of 128.30MiB at 2.10MiB/s ETA 00:42
```

O codigo extrai a porcentagem com expressao regular ou divisao de string e atualiza a barra de progresso correspondente na interface.

Apos a conclusao do download, o `yt-dlp` pode executar automaticamente o `ffmpeg` para fazer o merge de audio e video. O `QProcess` continua capturando a saida durante essa etapa e atualiza o status do item na lista para "Processando..." enquanto o merge ocorre.

**Componentes PySide6 envolvidos:**

- `QProcess`: executa e monitora o processo externo.
- Sinal `readyReadStandardOutput`: notifica quando ha nova saida disponivel para leitura.
- Sinal `finished`: notifica quando o processo terminou, com o codigo de saida.

---

## Cronograma de Desenvolvimento

O projeto e dividido em quatro fases sequenciais. Cada fase entrega funcionalidade testavel antes de avancar para a proxima, o que evita que erros de fundacao se acumulem.

---

### Fase 1 — Interface Base e Persistencia com JSON

**Objetivo:** Ter uma janela funcional que carrega e salva o estado dos downloads.

**Tarefas:**

1. Criar o projeto com estrutura de pastas organizada (`/src`, `/data`, `/assets`).
2. Instalar as dependencias: `PySide6`, `requests`.
3. Construir a janela principal com `QMainWindow`, incluindo:
   - Campo de texto (`QLineEdit`) para a URL.
   - Botao de adicionar download (`QPushButton`).
   - Tabela de downloads (`QTreeWidget`) com colunas: Nome do Arquivo, Progresso, Velocidade, Status.
4. Implementar a leitura do `downloads.json` na inicializacao. Se o arquivo nao existir, criar um vazio.
5. Implementar a funcao de salvar estado usando `json.dump()` com indentacao para o arquivo ser legivel.
6. Ao adicionar uma URL manualmente, o item deve aparecer na tabela com status "Na fila" e ser salvo no JSON.
7. Ao fechar e reabrir o programa, os itens devem ser restaurados da lista na tabela.

**Entrega da fase:** Programa abre, mostra downloads anteriores e salva novos sem crash.

---

### Fase 2 — Motor de Downloads Diretos com QThreadPool

**Objetivo:** Baixar arquivos HTTP/HTTPS reais em background, com progresso na interface.

**Tarefas:**

1. Criar a classe auxiliar `WorkerSignals(QObject)` com os sinais:
   - `progress = Signal(int, int)` — id do download e porcentagem atual.
   - `finished = Signal(int)` — id do download ao concluir.
   - `error = Signal(int, str)` — id e mensagem de erro.
2. Criar a classe `DownloadWorker(QRunnable)` que recebe id, URL e caminho de destino.
3. Implementar o metodo `run()` do worker:
   - Fazer requisicao com `requests.get(url, stream=True)`.
   - Ler o header `Content-Length` para saber o tamanho total.
   - Iterar sobre `response.iter_content(chunk_size=8192)` e escrever cada chunk no arquivo `.part`.
   - Calcular a porcentagem e emitir o sinal `progress`.
   - Ao concluir, renomear o arquivo de `.part` para o nome final e emitir `finished`.
4. Conectar os sinais do worker aos slots da interface para atualizar `QProgressBar` e o texto de status na tabela.
5. Instanciar `QThreadPool.globalInstance()` e usar `threadPool.start(worker)` para executar.
6. Implementar botao de pausar/cancelar: ao cancelar, uma flag no worker e ativada e o loop de chunks para.

**Entrega da fase:** Downloads HTTP funcionam em paralelo sem travar a interface, com barra de progresso em tempo real.

---

### Fase 3 — Integracao com yt-dlp via QProcess

**Objetivo:** Suportar downloads de YouTube e outras plataformas de streaming.

**Tarefas:**

1. Adicionar funcao `is_stream_url(url: str) -> bool` que verifica se a URL contem dominios suportados pelo yt-dlp (youtube.com, youtu.be, vimeo.com, twitch.tv, etc).
2. Verificar se o `yt-dlp` esta instalado no sistema. Se nao estiver, exibir uma mensagem orientando o usuario a instalar.
3. Criar o metodo `start_yt_dlp_download(id, url, output_path)`:
   - Instanciar `QProcess`.
   - Configurar o comando com os argumentos corretos.
   - Conectar `readyReadStandardOutput` a funcao `on_yt_dlp_output`.
   - Conectar `finished` a funcao `on_yt_dlp_finished`.
   - Chamar `process.start()`.
4. Implementar `on_yt_dlp_output`:
   - Ler o buffer: `process.readAllStandardOutput().data().decode("utf-8")`.
   - Fazer o parse da linha para extrair a porcentagem.
   - Emitir ou chamar diretamente a atualizacao da barra de progresso.
5. Implementar `on_yt_dlp_finished(exit_code)`:
   - Se `exit_code == 0`, marcar o download como concluido.
   - Caso contrario, marcar como erro e exibir mensagem.
6. Manter uma referencia para cada `QProcess` ativo em um dicionario `{id: QProcess}` para poder cancelar o processo se necessario.

**Entrega da fase:** Links do YouTube sao baixados com progresso exibido, sem travar a interface.

---

### Fase 4 — Finalizacao, Protecao Contra Concorrencia e Exportacao CSV

**Objetivo:** Tornar o sistema robusto para uso real e adicionar o relatorio de historico.

**Tarefas:**

1. Adicionar um `QMutex` global para proteger todas as operacoes de leitura e escrita no `downloads.json`. Toda funcao que modifica o arquivo deve chamar `mutex.lock()` antes e `mutex.unlock()` depois (ou usar um `QMutexLocker` para garantir o desbloqueio mesmo em caso de excecao).
2. Revisar todos os pontos do codigo onde o JSON e modificado e aplicar o mutex.
3. Implementar o botao "Exportar Historico":
   - Filtrar os downloads com status `concluido` no estado atual.
   - Abrir um `QFileDialog` para o usuario escolher onde salvar o CSV.
   - Usar `csv.DictWriter` para escrever o cabecalho e as linhas.
4. Adicionar tratamento de erros em todos os fluxos criticos:
   - Timeout de conexao no `requests.get`.
   - URL invalida ou inacessivel.
   - Espaco em disco insuficiente.
   - Processo `yt-dlp` encerrado com erro.
5. Revisar a interface para garantir que:
   - Downloads com erro exibam o motivo do erro ao passar o mouse.
   - O botao de cancelar funcione para os dois tipos de download (worker e QProcess).
   - O programa peca confirmacao antes de cancelar um download em andamento.
6. Realizar testes manuais cobrindo os cenarios:
   - Baixar dois arquivos diretos simultaneamente.
   - Pausar e retomar (fechar e reabrir o programa).
   - Exportar o historico com zero itens e com varios itens.
   - Colar uma URL invalida.

**Entrega da fase:** Sistema completo, estavel e pronto para uso.

---

## Dependencias do Projeto

| Dependencia | Versao Minima | Finalidade |
|---|---|---|
| Python | 3.10 | Linguagem principal |
| PySide6 | 6.5 | Interface grafica e threading |
| requests | 2.28 | Requisicoes HTTP para downloads diretos |
| yt-dlp | Mais recente | Download de streams e videos |
| ffmpeg | Qualquer | Merge de audio e video (usado pelo yt-dlp) |

As dependencias Python podem ser instaladas via:

```
pip install PySide6 requests
pip install yt-dlp
```

O `ffmpeg` deve ser instalado separadamente no sistema operacional e estar disponivel no PATH.

---

## Estrutura de Pastas Sugerida

```
download-manager/
  src/
    main.py               # Ponto de entrada, instancia o QApplication
    window.py             # Classe da janela principal (QMainWindow)
    worker.py             # DownloadWorker (QRunnable) e WorkerSignals
    process_manager.py    # Logica do QProcess para yt-dlp
    state.py              # Leitura e gravacao do downloads.json com mutex
    exporter.py           # Exportacao do historico para CSV
  data/
    downloads.json        # Estado persistido dos downloads
  assets/
    icon.png              # Icone do aplicativo
  requirements.txt
  README.md
  ARCHITECTURE.md
```