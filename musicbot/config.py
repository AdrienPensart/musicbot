import configparser
import logging
from functools import cache
from pathlib import Path
from typing import Final

import colorlog
from attr import frozen

from musicbot.exceptions import MusicbotError

logger = logging.getLogger(__name__)

DEFAULT_CONFIG: Final[str] = "~/musicbot.ini"
DEFAULT_LOG: Final[str | None] = None
DEFAULT_COLOR: Final[bool] = True
DEFAULT_DEBUG: Final[bool] = False
DEFAULT_INFO: Final[bool] = False
DEFAULT_WARNING: Final[bool] = False
DEFAULT_ERROR: Final[bool] = False
DEFAULT_CRITICAL: Final[bool] = False
DEFAULT_VERBOSITY: Final[str] = "warning"
DEFAULT_QUIET: Final[bool] = False

VERBOSITIES = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


@frozen(hash=True)
class Config:
    log: str | None = DEFAULT_LOG
    color: bool = DEFAULT_COLOR
    quiet: bool = True
    debug: bool = DEFAULT_DEBUG
    info: bool = DEFAULT_INFO
    warning: bool = DEFAULT_WARNING
    error: bool = DEFAULT_ERROR
    critical: bool = DEFAULT_CRITICAL
    config: str = DEFAULT_CONFIG
    level: int = VERBOSITIES[DEFAULT_VERBOSITY]

    def __attrs_post_init__(self) -> None:
        verbosity = "warning"
        if self.debug:
            verbosity = "debug"
        if self.info:
            verbosity = "info"
        if self.warning:
            verbosity = "warning"
        if self.error:
            verbosity = "error"
        if self.critical:
            verbosity = "critical"

        level = VERBOSITIES.get(verbosity, logging.WARNING)
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)
        stream_handler.setFormatter(
            colorlog.ColoredFormatter(
                fmt="\r%(log_color)s%(name)s | %(asctime)s | %(levelname)s | %(message)s\033[K",
                datefmt="%Y-%d-%d %H:%M:%S",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                },
            )
        )
        root_logger.handlers = []
        if self.log:
            log_path = Path(self.log).expanduser()
            try:
                file_handler = logging.FileHandler(log_path)
                root_logger.handlers.append(file_handler)
            except PermissionError as e:
                raise MusicbotError(f"Unable to write log file {log_path}") from e
        root_logger.handlers.append(stream_handler)

    @cache
    def _configfile(self) -> configparser.ConfigParser:
        file = configparser.ConfigParser()
        _ = file.read(Path(self.config).expanduser())
        if "musicbot" not in file:
            logger.warning(f"[musicbot] section is not present in {self.config}")
        return file

    @property
    def configfile(self) -> configparser.ConfigParser:
        return self._configfile()

    def write(self) -> None:
        with open(Path(self.config).expanduser(), "w", encoding="utf8") as output_config:
            self.configfile.write(output_config)
