import os
import logging
import configparser
import attr
import click
import colorlog
from cached_property import cached_property
from click_option_group import optgroup
from click_skeleton import ExpandedPath
from click_skeleton.helpers import str2bool


logger = logging.getLogger(__name__)

verbosities = {
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

DEFAULT_LOG = None
MB_LOG = 'MB_LOG'
log_option = [
    optgroup.option(
        '--log', '-l',
        help='Log file path',
        type=ExpandedPath(writable=True, dir_okay=False),
        envvar=MB_LOG,
        default=DEFAULT_LOG,
        show_default=True,
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
        type=click.Choice(verbosities.keys()),
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
    log: str = DEFAULT_LOG
    quiet: bool = DEFAULT_QUIET
    debug: bool = DEFAULT_DEBUG
    info: bool = DEFAULT_INFO
    timings: bool = DEFAULT_TIMINGS
    verbosity: str = DEFAULT_VERBOSITY
    config: str = DEFAULT_CONFIG
    level: int = verbosities[DEFAULT_VERBOSITY]

    def set(self, config=None, debug=None, info=None, timings=None, quiet=None, verbosity=None, log=None):
        self.config = config if config is not None else os.getenv(MB_CONFIG, DEFAULT_CONFIG)
        self.log = log if log is not None else os.getenv(MB_LOG, DEFAULT_LOG)
        self.quiet = quiet if quiet is not None else str2bool(os.getenv(MB_QUIET, str(DEFAULT_QUIET)))
        self.debug = debug if debug is not None else str2bool(os.getenv(MB_DEBUG, str(DEFAULT_DEBUG)))
        self.info = info if info is not None else str2bool(os.getenv(MB_INFO, str(DEFAULT_INFO)))
        self.timings = timings if timings is not None else str2bool(os.getenv(MB_TIMINGS, str(DEFAULT_TIMINGS)))
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

        if self.log is not None:
            fh = logging.FileHandler(self.log)
            fh.setLevel(logging.DEBUG)
            logging.getLogger().addHandler(fh)
        logger.debug(self)

    @cached_property
    def configfile(self):
        file = configparser.ConfigParser()
        file.read(self.config)
        valid_sections = ('musicbot', 'spotify')
        for section in valid_sections:
            if section not in file:
                logger.warning(f'[{section}] section is not present in {self.config}')
        return file

    def write(self):
        with open(self.config, 'w') as output_config:
            self.configfile.write(output_config)


config = Config()
