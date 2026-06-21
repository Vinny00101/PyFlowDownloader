# Changelog

Todas as mudanças relevantes do PyFlowDownloader serão documentadas aqui.

O projeto segue versionamento semântico: `MAJOR.MINOR.PATCH`.

## [0.4.0] - 2026-06-21

- Adicionado fluxo assistido para instalação do FFmpeg pelo próprio programa.
- O aplicativo agora detecta se o FFmpeg está disponível por caminho salvo ou busca automática no sistema antes de iniciar o uso.
- Quando o FFmpeg não é encontrado, a interface oferece instalação automática e permite escolher a pasta de destino.
- Implementado download do FFmpeg em segundo plano com barra de progresso e mensagens de status durante download e extração.
- Após a extração, o programa localiza o binário `ffmpeg.exe`, salva o caminho em `tools.ffmpeg_path` e reutiliza essa configuração nas próximas execuções.
- O caminho instalado/configurado do FFmpeg agora é repassado ao `yt-dlp` via `ffmpeg_location`, permitindo downloads em alta qualidade, merge de vídeo/áudio e conversão para MP3 sem configuração manual.
- Adicionada busca ampliada por FFmpeg em locais comuns, incluindo `PATH`, `C:/ffmpeg`, APPDATA do PyFlowDownloader, Downloads e Documents.
- Adicionada centralização das informações do aplicativo em `core/app_info.py`, incluindo nome, versão, descrição e caminho do ícone.
- Adicionada exibição da versão do programa no canto inferior direito da tela principal.
- Atualizado o visual da aplicação com janela principal sem moldura nativa, titlebar customizada, botões SVG de minimizar, maximizar/restaurar e fechar.
- Adicionadas bordas arredondadas e borda externa discreta na janela principal quando não está maximizada.
- Refinados os temas claro e escuro com nova paleta de cores, menor contraste no tema claro e aparência escura mais moderna.
- Melhorados botões, abas, campos, combos, tabelas, cards de download, painel de logs e mensagens do sistema para manter contraste correto nos dois temas.
- Corrigidos problemas visuais de bordas em containers, tabela de histórico, header da tabela, combos e cantos da janela.
- Refeito o sidebar de configurações com hierarquia visual mais limpa, grupos expansíveis e ícones SVG de chevron.
- Ajustado o comportamento do sidebar de configurações para que `Aparência`, `Downloads` e `Ferramentas` sejam apenas grupos, enquanto as páginas ficam nos itens internos.
- Adicionados ícones SVG para controles da janela e indicadores de navegação.

## [0.3.0] - 2026-05-26

- Armazenamento persistente de configurações via JSON na pasta APPDATA (`core/settings_manager.py`).
- Configuração do caminho do FFmpeg e funcionalidade de teste.
- Verificação e atualização da versão do `yt-dlp` somente em modo de desenvolvimento.
- Configurações de download: caminho padrão, formato, qualidade e downloads simultâneos.
- Tradução centralizada de erros do `yt-dlp` em `core/yt_dlp_errors.py` para mensagens mais amigáveis ao usuário.
- Tratamento de erros e feedback do usuário aprimorados durante todo o processo de download.
- Reorganização incremental da arquitetura PySide6 com camada `ui/slots` para separar slots da montagem das telas e dos controllers.
- Migração da composição visual principal para `ui/views`, deixando `MainWindow` focada em criar dependências e conectar sinais.
- Extração de utilitários em `ui/utils` para constantes, conexão/desconexão de sinais, logging opcional e criação de widgets recorrentes.
- Limpeza de código não utilizado após a reorganização, incluindo compatibilidades antigas de `ui/layouts` e `ui/utils/constant.py`.

## [0.2.0] - 2026-05-25

- Adicionando logo do PyFlowDownloader
- Adicionada a página de tema nas configurações.
- Adicionada opção para visualizar a versão instalada do `yt-dlp`.
- Adicionada opção para atualizar o `yt-dlp` pela interface.
- Adicionada tradução amigável para erros comuns do `yt-dlp`.
- Adicionado log de erro de download no painel de logs.
- Ajustado `QueuePanel` para evitar repetir o mesmo erro várias vezes.
- Melhorado o controller de configurações para executar ações de ferramentas.

## [v0.1.0] 23/05/2026

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

## Como Criar Uma Versão

1. Atualize este arquivo com as mudanças da nova versão.
2. Crie uma tag seguindo SemVer.
3. Envie a tag para o GitHub.

```bash
git tag v0.1.0
git push origin v0.1.0
```

Ao receber a tag, o GitHub Actions gera o `.zip` e cria uma Release.
