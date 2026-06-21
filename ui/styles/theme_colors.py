# theme_colors.py
# Paletas de cores centralizadas.
# Cada dicionário mapeia tokens semânticos para
# valores hex. Edite aqui para mudar as cores
# sem tocar na estrutura do tema.

DARK_COLORS = {
    # Backgrounds
    "bg_base":       "#050506",
    "bg_surface":    "#0b0b0d",
    "bg_elevated":   "#121216",

    # Borders
    "border":        "#26262d",
    "window_border": "#3f3f46",

    # Text
    "text_primary":  "#f4f4f5",
    "text_muted":    "#a1a1aa",
    "text_subtle":   "#71717a",

    # Accent / Brand
    "accent":        "#8bff9f",
    "accent_hover":  "#63e87b",
    "accent_press":  "#45c75e",

    # Semantic
    "success":       "#74e291",
    "danger":        "#fb7185",
    "danger_hover":  "#f43f5e",

    # Secondary button
    "secondary":     "#17171c",
    "secondary_hover": "#22222a",

    # Selection
    "selection":     "#1f3b2a",

    # On-accent (text sobre fundo colorido)
    "on_accent":     "#041007",
    "on_danger":     "#ffffff",
}

LIGHT_COLORS = {
    # Backgrounds
    "bg_base":       "#f6f6f4",
    "bg_surface":    "#ffffff",
    "bg_elevated":   "#eeeeeb",

    # Borders
    "border":        "#ddddda",
    "window_border": "#c7c7c2",

    # Text
    "text_primary":  "#27272a",
    "text_muted":    "#52525b",
    "text_subtle":   "#85858f",

    # Accent / Brand
    "accent":        "#2f9e44",
    "accent_hover":  "#2b8a3e",
    "accent_press":  "#237032",

    # Semantic
    "success":       "#2f9e44",
    "danger":        "#dc5a65",
    "danger_hover":  "#c73f4d",

    # Secondary button
    "secondary":     "#f2f2ef",
    "secondary_hover": "#e8e8e4",

    # Selection
    "selection":     "#dcefdc",

    # On-accent (texto sobre fundo colorido)
    "on_accent":     "#ffffff",
    "on_danger":     "#ffffff",
}

THEMES: dict[str, dict[str, str]] = {
    "dark":  DARK_COLORS,
    "light": LIGHT_COLORS,
}
