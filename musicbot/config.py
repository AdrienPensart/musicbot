import logging
import os
import time
import inspect
import functools
import configparser
from os import PathLike
from typing import Union, Optional, Any
import attr
import click
import colorlog  # type: ignore
from click_skeleton.helpers import str2bool, seconds_to_human

logger = logging.getLogger(__name__)

VERBOSITIES = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}

DEFAULT_CHECK_VERSION = False
DEFAULT_CONFIG = '~/musicbot.ini'
DEFAULT_LOG = ''
DEFAULT_DEBUG = False
DEFAULT_INFO = False
DEFAULT_WARNING = False
DEFAULT_ERROR = False
DEFAULT_CRITICAL = False
DEFAULT_TIMINGS = False
DEFAULT_VERBOSITY = 'warning'
DEFAULT_QUIET = False

MB_CHECK_VERSION = 'MB_CHECK_VERSION'
MB_CONFIG = 'MB_CONFIG'
MB_LOG = 'MB_LOG'
MB_DEBUG = 'MB_DEBUG'
MB_INFO = 'MB_INFO'
MB_WARNING = 'MB_WARNING'
MB_ERROR = 'MB_ERROR'
MB_CRITICAL = 'MB_CRITICAL'
MB_TIMINGS = 'MB_TIMINGS'
MB_VERBOSITY = 'MB_VERBOSITY'
MB_QUIET = 'MB_QUIET'


@attr.s(auto_attribs=True)
class Config:
    log: Optional[Union[str, PathLike]] = DEFAULT_LOG
    check_version: bool = DEFAULT_CHECK_VERSION
    quiet: bool = DEFAULT_QUIET
    debug: bool = DEFAULT_DEBUG
    info: bool = DEFAULT_INFO
    warning: bool = DEFAULT_WARNING
    error: bool = DEFAULT_ERROR
    critical: bool = DEFAULT_CRITICAL
    timings: bool = DEFAULT_TIMINGS
    verbosity: str = DEFAULT_VERBOSITY
    config: str = DEFAULT_CONFIG
    level: int = VERBOSITIES[DEFAULT_VERBOSITY]

    def __attrs_post_init__(self) -> None:
        self.check_version = str2bool(os.getenv(MB_CHECK_VERSION, 'true'))

    def set(
        self,
        config: Optional[str] = None,
        debug: Optional[bool] = None,
        info: Optional[bool] = None,
        warning: Optional[bool] = None,
        error: Optional[bool] = None,
        critical: Optional[bool] = None,
        timings: Optional[bool] = None,
        quiet: Optional[bool] = None,
        verbosity: Optional[str] = None,
        log: Optional[Union[str, PathLike]] = None,
    ) -> None:
        self.config = config if config is not None else os.environ.get(MB_CONFIG, DEFAULT_CONFIG)
        self.quiet = quiet if quiet is not None else str2bool(os.environ.get(MB_QUIET, str(DEFAULT_QUIET)))
        self.debug = debug if debug is not None else str2bool(os.environ.get(MB_DEBUG, str(DEFAULT_DEBUG)))
        self.info = info if info is not None else str2bool(os.environ.get(MB_INFO, str(DEFAULT_INFO)))
        self.warning = warning if warning is not None else str2bool(os.environ.get(MB_WARNING, str(DEFAULT_WARNING)))
        self.error = error if error is not None else str2bool(os.environ.get(MB_ERROR, str(DEFAULT_ERROR)))
        self.critical = critical if critical is not None else str2bool(os.environ.get(MB_CRITICAL, str(DEFAULT_CRITICAL)))
        self.timings = timings if timings is not None else str2bool(os.environ.get(MB_TIMINGS, str(DEFAULT_TIMINGS)))
        self.verbosity = verbosity if verbosity is not None else os.environ.get(MB_VERBOSITY, DEFAULT_VERBOSITY)
        self.log = (log if log is not None else os.environ.get(MB_LOG, DEFAULT_LOG)) or None

        if self.debug:
            self.verbosity = 'debug'
        if self.info:
            self.verbosity = 'info'
        if self.warning:
            self.verbosity = 'warning'
        if self.error:
            self.verbosity = 'error'
        if self.critical:
            self.verbosity = 'critical'

        self.level = VERBOSITIES.get(self.verbosity, logging.WARNING)
        root_logger = logging.getLogger()
        root_logger.setLevel(self.level)
        handler = logging.StreamHandler()
        handler.setLevel(self.level)
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
        root_logger.addHandler(handler)

        if self.log:
            fh = logging.FileHandler(self.log)
            fh.setLevel(logging.DEBUG)
            logging.getLogger().addHandler(fh)
            logger.debug(self)

    @functools.cached_property
    def configfile(self) -> configparser.ConfigParser:
        file = configparser.ConfigParser()
        file.read(self.config)
        valid_sections = ('musicbot', 'spotify')
        for section in valid_sections:
            if section not in file:
                logger.warning(f'[{section}] section is not present in {self.config}')
        return file

    def write(self) -> None:
        with open(self.config, 'w') as output_config:
            self.configfile.write(output_config)

    def timeit(self, *wrapper_args: Any, **wrapper_kwargs: Any) -> Any:
        func = None
        if len(wrapper_args) == 1 and callable(wrapper_args[0]):
            func = wrapper_args[0]
        if func:
            always = False
            on_success = False
            on_config = True
        else:
            always = wrapper_kwargs.get('always', False)
            on_success = wrapper_kwargs.get('on_success', False)
            on_config = wrapper_kwargs.get('on_config', True)

        def real_timeit(func: Any) -> Any:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                start = int(time.time())
                result = None
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    end = int(time.time())
                    for_human = seconds_to_human(end - start)

                    if self.info or self.debug:
                        args_values = []
                        argspec = inspect.getfullargspec(func)
                        # go through each position based argument
                        counter = 0
                        if argspec.args and isinstance(argspec.args, list):
                            for arg in args:
                                # when you run past the formal positional arguments
                                try:
                                    args_values.append(str(argspec.args[counter]) + " = " + str(arg))
                                    counter += 1
                                except IndexError:
                                    # then fallback to using the positional varargs name
                                    if argspec.varargs:
                                        varargsname = argspec.varargs
                                        args_values.append("*" + varargsname + " = " + str(arg))

                        # finally show the named varargs
                        for k, v in kwargs.items():
                            args_values.append(k + " = " + str(v))

                        args_values_str = '|'.join(args_values)
                        if argspec.annotations.get('return', None) is None:
                            timing = f'(timings) {func.__module__}.{func.__qualname__} ({args_values_str}): {for_human}'
                        else:
                            timing = f'(timings) {func.__module__}.{func.__qualname__} ({args_values_str}): {for_human} | result = {result}'
                    else:
                        timing = f'(timings) {func.__module__}.{func.__qualname__} : {for_human}'
                    if always or (on_success and result) or (on_config and self.timings):
                        click.secho(timing, fg="magenta", bold=True, err=True)
            return wrapper
        return real_timeit(func) if func else real_timeit


config = Config()
