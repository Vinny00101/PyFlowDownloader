# theme_colors.py
# Paletas de cores centralizadas.
# Cada dicionário mapeia tokens semânticos para
# valores hex. Edite aqui para mudar as cores
# sem tocar na estrutura do tema.

DARK_COLORS = {
    # Backgrounds
    "bg_base":       "#1a1b26",
    "bg_surface":    "#20212d",
    "bg_elevated":   "#1f2335",

    # Borders
    "border":        "#414868",

    # Text
    "text_primary":  "#c0caf5",
    "text_muted":    "#a9b1d6",
    "text_subtle":   "#565f89",

    # Accent / Brand
    "accent":        "#5ccb5f",
    "accent_hover":  "#009929",
    "accent_press":  "#006414",

    # Semantic
    "success":       "#9ece6a",
    "danger":        "#f7768e",
    "danger_hover":  "#ff9eaf",

    # Secondary button
    "secondary":     "#414868",
    "secondary_hover": "#565f89",

    # Selection
    "selection":     "#364a82",

    # On-accent (text sobre fundo colorido)
    "on_accent":     "#1a1b26",
    "on_danger":     "#1a1b26",
}

LIGHT_COLORS = {
    # Backgrounds
    "bg_base":       "#f5f7fb",
    "bg_surface":    "#ffffff",
    "bg_elevated":   "#f1f5f9",

    # Borders
    "border":        "#cbd5e1",

    # Text
    "text_primary":  "#1e293b",
    "text_muted":    "#475569",
    "text_subtle":   "#94a3b8",

    # Accent / Brand
    "accent":        "#5ccb5f",
    "accent_hover":  "#009929",
    "accent_press":  "#006414",

    # Semantic
    "success":       "#22c55e",
    "danger":        "#ef4444",
    "danger_hover":  "#dc2626",

    # Secondary button
    "secondary":     "#e2e8f0",
    "secondary_hover": "#cbd5e1",

    # Selection
    "selection":     "#bfdbfe",

    # On-accent (texto sobre fundo colorido)
    "on_accent":     "#ffffff",
    "on_danger":     "#ffffff",
}

THEMES: dict[str, dict[str, str]] = {
    "dark":  DARK_COLORS,
    "light": LIGHT_COLORS,
}
