import configparser
import functools
import logging
import sys
from pathlib import Path
from typing import Optional

import attr
import colorlog
import progressbar  # type: ignore

from musicbot.exceptions import MusicbotError

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = '~/musicbot.ini'
DEFAULT_LOG: Optional[str] = None
DEFAULT_COLOR = True
DEFAULT_DEBUG = False
DEFAULT_INFO = False
DEFAULT_WARNING = False
DEFAULT_ERROR = False
DEFAULT_CRITICAL = False
DEFAULT_TIMINGS = False
DEFAULT_VERBOSITY = 'warning'
DEFAULT_QUIET = False

VERBOSITIES = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}


@attr.s(auto_attribs=True, frozen=True)
class Config:
    log: Optional[str] = DEFAULT_LOG
    color: bool = DEFAULT_COLOR
    quiet: bool = True
    debug: bool = DEFAULT_DEBUG
    info: bool = DEFAULT_INFO
    warning: bool = DEFAULT_WARNING
    error: bool = DEFAULT_ERROR
    critical: bool = DEFAULT_CRITICAL
    timings: bool = DEFAULT_TIMINGS
    config: str = DEFAULT_CONFIG
    level: int = VERBOSITIES[DEFAULT_VERBOSITY]

    def __attrs_post_init__(self) -> None:
        verbosity = 'warning'
        if self.debug:
            verbosity = 'debug'
        if self.info:
            verbosity = 'info'
        if self.warning:
            verbosity = 'warning'
        if self.error:
            verbosity = 'error'
        if self.critical:
            verbosity = 'critical'

        level = VERBOSITIES.get(verbosity, logging.WARNING)
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        if not self.quiet and "pytest" not in sys.modules:
            progressbar.streams.wrap(stderr=True, stdout=True)
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(
            colorlog.ColoredFormatter(
                fmt='%(log_color)s%(name)s | %(asctime)s | %(levelname)s | %(message)s',
                datefmt='%Y-%d-%d %H:%M:%S',
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                },
            )
        )
        root_logger.handlers = []
        root_logger.addHandler(handler)
        if self.log:
            log_path = Path(self.log).expanduser()
            try:
                fh = logging.FileHandler(log_path)
                fh.setLevel(logging.DEBUG)
                logging.getLogger().addHandler(fh)
                logger.debug(self)
            except PermissionError as e:
                raise MusicbotError(f"Unable to write log file {log_path}") from e

    @functools.cached_property
    def configfile(self) -> configparser.ConfigParser:
        file = configparser.ConfigParser()
        file.read(Path(self.config).expanduser())
        if 'musicbot' not in file:
            logger.warning(f'[musicbot] section is not present in {self.config}')
        return file

    def write(self) -> None:
        with open(Path(self.config).expanduser(), 'w', encoding="utf8") as output_config:
            self.configfile.write(output_config)
