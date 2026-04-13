from __future__ import annotations

import logging
import os
import sys
from dataclasses import dataclass


SUCCESS_LEVEL = 25
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")


@dataclass(frozen=True)
class _Style:
    color: str
    icon: str


class _ColorFormatter(logging.Formatter):
    RESET = "\033[0m"
    DIM = "\033[2m"

    STYLES: dict[int, _Style] = {
        logging.DEBUG: _Style("\033[38;5;244m", "•"),
        logging.INFO: _Style("\033[38;5;45m", "ℹ"),
        SUCCESS_LEVEL: _Style("\033[38;5;47m", "✓"),
        logging.WARNING: _Style("\033[38;5;214m", "⚠"),
        logging.ERROR: _Style("\033[38;5;203m", "✖"),
        logging.CRITICAL: _Style("\033[1;37;41m", "‼"),
    }

    def __init__(self, use_color: bool) -> None:
        super().__init__(datefmt="%H:%M:%S")
        self.use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        style = self.STYLES.get(record.levelno, self.STYLES[logging.INFO])
        timestamp = self.formatTime(record, self.datefmt)
        level = record.levelname.ljust(8)
        name = record.name
        message = record.getMessage()
        if self.use_color:
            return (
                f"{self.DIM}{timestamp}{self.RESET} "
                f"{style.color}{style.icon} {level}{self.RESET} "
                f"{self.DIM}{name}{self.RESET} {message}"
            )
        return f"{timestamp} {style.icon} {level} {name} {message}"


class AppLogger:
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def debug(self, message: str, *args, **kwargs) -> None:
        self._logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        self._logger.info(message, *args, **kwargs)

    def success(self, message: str, *args, **kwargs) -> None:
        self._logger.log(SUCCESS_LEVEL, message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        self._logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        self._logger.error(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs) -> None:
        self._logger.exception(message, *args, **kwargs)

    def banner(self, title: str, width: int = 78, char: str = "═") -> None:
        rule = char * width
        self.info(rule)
        self.success(title)
        self.info(rule)


_CONFIGURED = False


def _supports_color() -> bool:
    if os.getenv("NO_COLOR"):
        return False
    forced = os.getenv("FORCE_COLOR")
    if forced is not None:
        return forced != "0"
    return bool(getattr(sys.stderr, "isatty", lambda: False)())


def _configure_root() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    handler = logging.StreamHandler()
    handler.setFormatter(_ColorFormatter(use_color=_supports_color()))

    root = logging.getLogger("app")
    root.setLevel(os.getenv("APP_LOG_LEVEL", "INFO").upper())
    root.handlers.clear()
    root.addHandler(handler)
    root.propagate = False
    _CONFIGURED = True


def get_logger(name: str) -> AppLogger:
    _configure_root()
    logger = logging.getLogger(name)
    if not logger.name.startswith("app"):
        logger = logging.getLogger(f"app.{name}")
    return AppLogger(logger)

