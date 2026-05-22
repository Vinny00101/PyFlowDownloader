from typing import Protocol, runtime_checkable


@runtime_checkable
class LoggerProtocol(Protocol):
    """Interface mínima para um componente que aceita logs."""

    def log(self, message: str) -> None: ...
