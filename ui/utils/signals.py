from collections.abc import Iterable
from typing import Any

SignalSlot = tuple[Any, Any]


def connect_many(connections: Iterable[SignalSlot]) -> None:
    for signal, slot in connections:
        signal.connect(slot)


def disconnect_many(connections: Iterable[SignalSlot]) -> None:
    for signal, slot in connections:
        try:
            signal.disconnect(slot)
        except TypeError:
            pass
