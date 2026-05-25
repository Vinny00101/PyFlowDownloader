"""Tradução amigável para mensagens comuns do yt-dlp."""

from __future__ import annotations


_ERROR_TRANSLATIONS: tuple[tuple[tuple[str, ...], str], ...] = (
    (
        ("sign in to confirm", "not a bot"),
        (
            "O YouTube pediu login para confirmar que o acesso não é automatizado. "
            "Atualize o yt-dlp e, se continuar, configure cookies do navegador."
        ),
    ),
    (
        ("sign in", "cookies"),
        (
            "O site pediu login/cookies para liberar o vídeo. "
            "Atualize o yt-dlp e use cookies do navegador quando necessário."
        ),
    ),
    (
        ("cookies",),
        (
            "O site precisa de cookies do navegador para acessar esse conteúdo. "
            "Configure os cookies e tente novamente."
        ),
    ),
    (
        ("private video",),
        "Este vídeo é privado ou sua conta não tem permissão para acessá-lo.",
    ),
    (
        ("video unavailable",),
        "Este vídeo está indisponível, removido ou bloqueado para a sua região.",
    ),
    (
        ("age-restricted",),
        (
            "Este conteúdo tem restrição de idade. "
            "Use cookies de uma conta autorizada para tentar baixar."
        ),
    ),
    (
        ("login required",),
        (
            "Esse conteúdo exige login. "
            "Configure cookies de uma conta autorizada e tente novamente."
        ),
    ),
    (
        ("too many requests",),
        (
            "O site recebeu muitas tentativas em pouco tempo e limitou o acesso. "
            "Aguarde alguns minutos antes de tentar novamente."
        ),
    ),
    (
        ("captcha",),
        (
            "O site pediu verificação/captcha. "
            "Atualize o yt-dlp e use cookies do navegador se o problema continuar."
        ),
    ),
    (
        ("drm",),
        "Este conteúdo usa proteção DRM e não pode ser baixado pelo yt-dlp.",
    ),
    (
        ("premium",),
        "Este conteúdo parece exigir uma assinatura ou conta autorizada.",
    ),
    (
        ("requested format is not available",),
        (
            "A qualidade/formato escolhido não está disponível para esse vídeo. "
            "Tente outra qualidade."
        ),
    ),
    (
        ("unsupported url",),
        "O link informado não é compatível com o yt-dlp.",
    ),
    (
        ("http error 403",),
        (
            "O site bloqueou o acesso ao arquivo (erro 403). "
            "Atualizar o yt-dlp ou usar cookies pode resolver."
        ),
    ),
    (
        ("http error 404",),
        "O arquivo ou vídeo não foi encontrado no servidor (erro 404).",
    ),
    (
        ("unable to download webpage",),
        (
            "Não foi possível carregar a página do vídeo. "
            "Verifique sua conexão e tente novamente."
        ),
    ),
    (
        ("timed out",),
        "A conexão demorou demais para responder. Tente novamente em alguns instantes.",
    ),
    (
        ("certificate verify failed",),
        (
            "Falha ao validar o certificado de segurança da conexão. "
            "Verifique data/hora do sistema e certificados instalados."
        ),
    ),
    (
        ("ffmpeg", "not found"),
        "O ffmpeg não foi encontrado. Configure o caminho do ffmpeg nas ferramentas.",
    ),
)


def translate_yt_dlp_error(error: object) -> str:
    """Retorna uma mensagem em português para erros conhecidos do yt-dlp."""
    original = str(error).strip()
    if not original:
        return "O yt-dlp retornou um erro desconhecido."

    normalized = original.lower()
    for fragments, message in _ERROR_TRANSLATIONS:
        if all(fragment in normalized for fragment in fragments):
            return f"{message}\nDetalhe técnico: {original}"

    if normalized.startswith("error:"):
        original = original[6:].strip()

    return f"O yt-dlp encontrou um erro: {original}"
