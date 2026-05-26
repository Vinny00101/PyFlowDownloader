from ui.protocols import LoggerProtocol


def log_if_available(logger: LoggerProtocol | None, message: str) -> None:
    if logger is not None:
        logger.log(message)
