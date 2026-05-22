from .manager import DownloadManagerProtocol
from .logger import LoggerProtocol
from .tasks import HistoryTaskProtocol, QueueTaskProtocol

__all__ = [
    "DownloadManagerProtocol",
    "LoggerProtocol",
    "HistoryTaskProtocol",
    "QueueTaskProtocol",
]
