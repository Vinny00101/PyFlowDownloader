from PySide6.QtWidgets import QLabel, QPushButton


def label(text: str, object_name: str | None = None, word_wrap: bool = False) -> QLabel:
    widget = QLabel(text)
    if object_name:
        widget.setObjectName(object_name)
    widget.setWordWrap(word_wrap)
    return widget


def card_title(text: str) -> QLabel:
    return label(text, object_name="cardTitle")


def subtitle(text: str, word_wrap: bool = True) -> QLabel:
    return label(text, object_name="subtitleLabel", word_wrap=word_wrap)


def secondary_button(text: str) -> QPushButton:
    button = QPushButton(text)
    button.setObjectName("secondaryBtn")
    return button
