import logging
import signal
import os
from pathlib import Path
import concurrent.futures as cf
import time
import inspect
import functools
import configparser
from typing import Optional, Any
import attr
import click
import progressbar  # type: ignore
import colorlog  # type: ignore
from click_skeleton.helpers import seconds_to_human
from musicbot.exceptions import MusicbotError
from musicbot.defaults import DEFAULT_MB_CONCURRENCY

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = Path('~/musicbot.ini')
DEFAULT_LOG: Optional[Path] = None
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
    log: Optional[Path] = DEFAULT_LOG
    quiet: bool = True
    debug: bool = DEFAULT_DEBUG
    info: bool = DEFAULT_INFO
    warning: bool = DEFAULT_WARNING
    error: bool = DEFAULT_ERROR
    critical: bool = DEFAULT_CRITICAL
    timings: bool = DEFAULT_TIMINGS
    config: Path = DEFAULT_CONFIG
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
        if not self.quiet:
            progressbar.streams.wrap_stderr()
            progressbar.streams.wrap_stdout()
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
            log_path = self.log.expanduser()
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
        config_path = self.config.expanduser()
        file.read(config_path)
        if 'musicbot' not in file:
            logger.warning(f'[musicbot] section is not present in {self.config}')
        return file

    def write(self) -> None:
        config_path = self.config.expanduser()
        with open(config_path, 'w') as output_config:
            self.configfile.write(output_config)


class Conf:
    config = Config()

    @classmethod
    def progressbar(cls, quiet=False, redirect_stderr=True, redirect_stdout=True, **pbar_options):
        if quiet or cls.config.quiet:
            return progressbar.NullBar(redirect_stderr=redirect_stderr, redirect_stdout=redirect_stdout, **pbar_options)
        return progressbar.ProgressBar(redirect_stderr=redirect_stderr, redirect_stdout=redirect_stdout, **pbar_options)

    @classmethod
    def parallel(cls, worker, items, quiet=False, concurrency=DEFAULT_MB_CONCURRENCY, **pbar_options):
        with cls.progressbar(max_value=len(items), quiet=quiet, redirect_stderr=True, redirect_stdout=True, **pbar_options) as pbar, \
             cf.ThreadPoolExecutor(max_workers=concurrency) as executor:
            try:
                def update_pbar(_):
                    try:
                        pbar.value += 1
                        pbar.update()
                    except KeyboardInterrupt as e:
                        logger.error(f"interrupted : {e}")
                        while True:
                            os.kill(os.getpid(), signal.SIGKILL)
                            os.killpg(os.getpid(), signal.SIGKILL)
                futures = []
                for item in items:
                    future = executor.submit(worker, item)
                    future.add_done_callback(update_pbar)
                    futures.append(future)
                cf.wait(futures)
                return [future.result() for future in futures if future.result() is not None]
            except KeyboardInterrupt as e:
                logger.error(f"interrupted : {e}")
                while True:
                    os.kill(os.getpid(), signal.SIGKILL)
                    os.killpg(os.getpid(), signal.SIGKILL)

    @classmethod
    def timeit(cls, *wrapper_args: Any, **wrapper_kwargs: Any) -> Any:
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

                    if cls.config.info or Conf.config.debug:
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
                    if always or (on_success and result) or (on_config and cls.config.timings):
                        click.secho(timing, fg="magenta", bold=True, err=True)
            return wrapper
        return real_timeit(func) if func else real_timeit
