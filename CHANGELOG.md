# Changelog

Todas as mudanças relevantes do PyFlowDownloader serão documentadas aqui.

O projeto segue versionamento semântico: `MAJOR.MINOR.PATCH`.

## [Unreleased]

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
