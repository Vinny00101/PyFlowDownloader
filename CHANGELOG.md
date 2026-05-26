# Changelog

Todas as mudanças relevantes do PyFlowDownloader serão documentadas aqui.

O projeto segue versionamento semântico: `MAJOR.MINOR.PATCH`.

## [Unreleased]

- Armazenamento persistente de configurações via JSON na pasta APPDATA (core/settings_manager.py)
- Configuração do caminho do FFmpeg e funcionalidade de teste
- Verificação e atualização da versão do yt-dlp (somente em modo de desenvolvimento)
- Configurações de download: caminho padrão, formato, qualidade e downloads simultâneos
- Tradução centralizada de erros do yt-dlp em core/yt_dlp_errors.py para mensagens mais amigáveis ​​ao usuário
- Tratamento de erros e feedback do usuário aprimorados durante todo o processo de download

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
