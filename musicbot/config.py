import os
import time
import inspect
import logging
import functools
import configparser
from os import PathLike
from typing import Union, Optional, Any
import attr
import click
import colorlog  # type: ignore
from click_option_group import optgroup  # type: ignore
from click_skeleton import ExpandedPath
from click_skeleton.helpers import str2bool, seconds_to_human


logger = logging.getLogger(__name__)

DEFAULT_CHECK_VERSION = False
MB_CHECK_VERSION = 'MB_CHECK_VERSION'

VERBOSITIES = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}

DEFAULT_CONFIG = '~/musicbot.ini'
MB_CONFIG = 'MB_CONFIG'
config_option = [
    optgroup.option(
        '--config', '-c',
        help='Config file path',
        type=ExpandedPath(writable=True, dir_okay=False),
        envvar=MB_CONFIG,
        default=DEFAULT_CONFIG,
        show_default=True,
    )
]

DEFAULT_LOG = ''
MB_LOG = 'MB_LOG'
log_option = [
    optgroup.option(
        '--log', '-l',
        help='Log file path',
        type=ExpandedPath(writable=True, dir_okay=False),
        envvar=MB_LOG,
        default=DEFAULT_LOG,
    )
]

DEFAULT_INFO = False
MB_INFO = 'MB_INFO'
info_option = [
    optgroup.option(
        '--info', '-i',
        help='Same as "--verbosity info"',
        envvar=MB_INFO,
        default=DEFAULT_INFO,
        is_flag=True,
        show_default=False,
    )
]

DEFAULT_DEBUG = False
MB_DEBUG = 'MB_DEBUG'
debug_option = [
    optgroup.option(
        '--debug', '-d',
        help='Be very verbose, same as "--verbosity debug" + hide progress bars',
        envvar=MB_DEBUG,
        default=DEFAULT_DEBUG,
        is_flag=True,
        show_default=True,
    )
]

DEFAULT_TIMINGS = False
MB_TIMINGS = 'MB_TIMINGS'
timings_option = [
    optgroup.option(
        '--timings', '-t',
        help='Set verbosity to info and show execution timings',
        envvar=MB_TIMINGS,
        default=DEFAULT_TIMINGS,
        is_flag=True,
        show_default=True,
    )
]

DEFAULT_VERBOSITY = 'warning'
MB_VERBOSITY = 'MB_VERBOSITY'
verbosity_option = [
    optgroup.option(
        '--verbosity', '-v',
        help='Verbosity levels',
        envvar=MB_VERBOSITY,
        default=DEFAULT_VERBOSITY,
        type=click.Choice(VERBOSITIES.keys()),
        show_default=True,
    )
]

DEFAULT_QUIET = False
MB_QUIET = 'MB_QUIET'
quiet_option = [
    optgroup.option(
        '--quiet', '-q',
        help='Disable progress bars',
        envvar=MB_QUIET,
        default=DEFAULT_QUIET,
        is_flag=True,
        show_default=True,
    )
]

options =\
    [optgroup.group('Config options')] +\
    config_option +\
    log_option +\
    info_option +\
    debug_option +\
    timings_option +\
    verbosity_option +\
    quiet_option


@attr.s(auto_attribs=True)
class Config:
    log: Optional[Union[str, PathLike]] = DEFAULT_LOG
    check_version: bool = DEFAULT_CHECK_VERSION
    quiet: bool = DEFAULT_QUIET
    debug: bool = DEFAULT_DEBUG
    info: bool = DEFAULT_INFO
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
        timings: Optional[bool] = None,
        quiet: Optional[bool] = None,
        verbosity: Optional[str] = None,
        log: Optional[Union[str, PathLike]] = None,
    ) -> None:
        self.config = config if config is not None else os.environ.get(MB_CONFIG, DEFAULT_CONFIG)
        self.quiet = quiet if quiet is not None else str2bool(os.environ.get(MB_QUIET, str(DEFAULT_QUIET)))
        self.debug = debug if debug is not None else str2bool(os.environ.get(MB_DEBUG, str(DEFAULT_DEBUG)))
        self.info = info if info is not None else str2bool(os.environ.get(MB_INFO, str(DEFAULT_INFO)))
        self.timings = timings if timings is not None else str2bool(os.environ.get(MB_TIMINGS, str(DEFAULT_TIMINGS)))
        self.verbosity = verbosity if verbosity is not None else os.environ.get(MB_VERBOSITY, DEFAULT_VERBOSITY)
        self.log = (log if log is not None else os.environ.get(MB_LOG, DEFAULT_LOG)) or None

        if self.timings or self.info:
            self.verbosity = 'info'
            self.quiet = True
        if self.debug:
            self.verbosity = 'debug'
            self.quiet = True

        self.level = VERBOSITIES[self.verbosity]
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
                    'CRITICAL': 'red,bg_white'},
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
                start = time.time()
                result = func(*args, **kwargs)
                for_human = seconds_to_human(time.time() - start)

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
                    timing = f'(timings) {func.__module__}.{func.__qualname__} ({args_values_str}): {for_human} | result = {result}'
                else:
                    timing = f'(timings) {func.__module__}.{func.__qualname__} : {for_human}'
                if always or (on_success and result) or (on_config and self.timings):
                    click.secho(timing, fg="magenta", bold=True)
                return result
            return wrapper
        return real_timeit(func) if func else real_timeit


config = Config()
