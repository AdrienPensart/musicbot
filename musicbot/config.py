import os
import getpass
import logging
import configparser
import attr
import click
import colorlog
from cached_property import cached_property
from click_option_group import optgroup
from . import lib


logger = logging.getLogger(__name__)
current_user = getpass.getuser()

MB_CONFIG = 'MB_CONFIG'
MB_LOG = 'MB_LOG'
MB_INFO = 'MB_INFO'
MB_DEBUG = 'MB_DEBUG'
MB_TIMINGS = 'MB_TIMINGS'
MB_VERBOSITY = 'MB_VERBOSITY'
MB_QUIET = 'MB_QUIET'
MB_COLORS = 'MB_COLORS'

DEFAULT_CONFIG = '~/musicbot.ini'
DEFAULT_LOG = None
DEFAULT_VERBOSITY = 'warning'
DEFAULT_QUIET = False
DEFAULT_DEBUG = False
DEFAULT_COLORS = True
DEFAULT_TIMINGS = False
DEFAULT_INFO = False


verbosities = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

config_option = [
    optgroup.option(
        '--config', '-c',
        help='Config file path',
        type=click.Path(),
        envvar=MB_CONFIG,
        default=DEFAULT_CONFIG,
        show_default=True
    )
]

log_option = [
    optgroup.option(
        '--log', '-l',
        help='Log file path',
        type=click.Path(),
        envvar=MB_LOG,
        default=DEFAULT_LOG,
        show_default=True
    )
]

info_option = [
    optgroup.option(
        '--info', '-i',
        help='Same as "--verbosity info"',
        envvar=MB_INFO,
        default=DEFAULT_INFO,
        is_flag=True,
        show_default=False
    )
]

debug_option = [
    optgroup.option(
        '--debug', '-d',
        help='Be very verbose, same as "--verbosity debug" + hide progress bars',
        envvar=MB_DEBUG,
        default=DEFAULT_DEBUG,
        is_flag=True,
        show_default=True
    )
]

timings_option = [
    optgroup.option(
        '--timings', '-t',
        help='Set verbosity to info and show execution timings',
        envvar=MB_TIMINGS,
        default=DEFAULT_TIMINGS,
        is_flag=True,
        show_default=True
    )
]

verbosity_option = [
    optgroup.option(
        '--verbosity', '-v',
        help='Verbosity levels',
        envvar=MB_VERBOSITY,
        default=DEFAULT_VERBOSITY,
        type=click.Choice(verbosities.keys()),
        show_default=True
    )
]

quiet_option = [
    optgroup.option(
        '--quiet', '-q',
        help='Disable progress bars',
        envvar=MB_QUIET,
        default=DEFAULT_QUIET,
        is_flag=True,
        show_default=True
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


def check_file_writable(fnm):
    if os.path.exists(fnm):
        if os.path.isfile(fnm):
            return os.access(fnm, os.W_OK)
        return False
    pdir = os.path.dirname(fnm)
    if not pdir:
        pdir = '.'
    return os.access(pdir, os.W_OK)


@attr.s
class Config:
    log = attr.ib(default=DEFAULT_LOG)
    quiet = attr.ib(default=DEFAULT_QUIET)
    debug = attr.ib(default=DEFAULT_DEBUG)
    info = attr.ib(default=DEFAULT_INFO)
    timings = attr.ib(default=DEFAULT_TIMINGS)
    verbosity = attr.ib(default=DEFAULT_VERBOSITY)
    config = attr.ib(default=DEFAULT_CONFIG)
    level = attr.ib(default=verbosities[DEFAULT_VERBOSITY])
    fmt = attr.ib(default='%(log_color)s%(name)s | %(asctime)s | %(levelname)s | %(message)s', repr=False)

    def set(self, config=None, debug=None, info=None, timings=None, quiet=None, verbosity=None, log=None):
        self.config = config if config is not None else os.getenv(MB_CONFIG, DEFAULT_CONFIG)
        self.config = os.path.expanduser(self.config)
        if not check_file_writable(self.config):
            logger.warning(f'No permission to write to {self.config} for current user {current_user}')

        self.log = log if log is not None else os.getenv(MB_LOG, DEFAULT_LOG)
        if self.log:
            self.log = os.path.expanduser(self.log)

        self.quiet = quiet if quiet is not None else lib.str2bool(os.getenv(MB_QUIET, str(DEFAULT_QUIET)))
        self.debug = debug if debug is not None else lib.str2bool(os.getenv(MB_DEBUG, str(DEFAULT_DEBUG)))
        self.info = info if info is not None else lib.str2bool(os.getenv(MB_INFO, str(DEFAULT_INFO)))
        self.timings = timings if timings is not None else lib.str2bool(os.getenv(MB_TIMINGS, str(DEFAULT_TIMINGS)))
        self.verbosity = verbosity if verbosity is not None else os.getenv(MB_VERBOSITY, DEFAULT_VERBOSITY)

        if self.timings or self.info:
            self.verbosity = 'info'
            self.quiet = True
        if self.debug:
            self.verbosity = 'debug'
            self.quiet = True

        self.level = verbosities[self.verbosity]
        root_logger = logging.getLogger()
        root_logger.setLevel(self.level)
        handler = logging.StreamHandler()
        handler.setLevel(self.level)
        handler.setFormatter(
            colorlog.ColoredFormatter(
                self.fmt,
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

        if self.log is not None:
            if check_file_writable(self.log):
                fh = logging.FileHandler(self.log)
                fh.setLevel(logging.DEBUG)
                logging.getLogger().addHandler(fh)
            else:
                logger.warning(f'No permission to write to {self.log} for current user {current_user}')
        logger.debug(self)

    @cached_property
    def configfile(self):
        file = configparser.ConfigParser()
        file.read(self.config)
        if 'musicbot' not in file:
            logger.warning(f'[musicbot] section is not present in {self.config}')
        if 'spotify' not in file:
            logger.warning(f'spotify section not present in {self.config}')
        return file

    def write(self):
        with open(self.config, 'w') as output_config:
            self.configfile.write(output_config)


config = Config()
