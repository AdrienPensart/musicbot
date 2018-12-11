import click
import asyncio
import os
import coloredlogs
import logging
import attr
import pwd
from . import lib

logger = logging.getLogger(__name__)
current_user = pwd.getpwuid(os.getuid()).pw_name

DEFAULT_LOG = '/var/log/musicbot.log'
MB_LOG = 'MB_LOG'
MB_DEBUG = 'MB_DEBUG'
MB_TIMINGS = 'MB_TIMINGS'
MB_VERBOSITY = 'MB_VERBOSITY'
MB_DRY = 'MB_DRY'
MB_QUIET = 'MB_QUIET'
MB_NO_COLORS = 'MB_NO_COLORS'

DEFAULT_VERBOSITY = 'warning'
DEFAULT_DRY = False
DEFAULT_QUIET = False
DEFAULT_DEBUG = False
DEFAULT_NO_COLORS = False
DEFAULT_TIMINGS = False
verbosities = {'debug': logging.DEBUG,
               'info': logging.INFO,
               'warning': logging.WARNING,
               'error': logging.ERROR,
               'critical': logging.CRITICAL}

options = [
    click.option('--log', help='Log file path', type=click.Path(), envvar=MB_LOG, default=DEFAULT_LOG, show_default=True),
    click.option('--debug', help='Be very verbose, same as --verbosity debug + hide progress bars', envvar=MB_DEBUG, default=DEFAULT_DEBUG, is_flag=True),
    click.option('--timings', help='Set verbosity to info and show execution timings', envvar=MB_TIMINGS, default=DEFAULT_TIMINGS, is_flag=True),
    click.option('--verbosity', help='Verbosity levels', envvar=MB_VERBOSITY, default=DEFAULT_VERBOSITY, type=click.Choice(verbosities.keys()), show_default=True),
    click.option('--dry', help='Take no real action', envvar=MB_DRY, default=DEFAULT_DRY, is_flag=True),
    click.option('--quiet', help='Disable progress bars', envvar=MB_QUIET, default=DEFAULT_QUIET, is_flag=True),
    click.option('--no-colors', help='Disable colorized output', envvar=MB_NO_COLORS, default=DEFAULT_NO_COLORS, is_flag=True),
]


def check_file_writable(fnm):
    if os.path.exists(fnm):
        # path exists
        if os.path.isfile(fnm):
            return os.access(fnm, os.W_OK)
        else:
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
    timings = attr.ib(default=DEFAULT_TIMINGS)
    dry = attr.ib(default=DEFAULT_DRY)
    no_colors = attr.ib(default=DEFAULT_NO_COLORS)
    verbosity = attr.ib(default=DEFAULT_VERBOSITY)
    fmt = attr.ib(default="%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s")

    def set(self, debug=None, timings=None, dry=None, quiet=None, verbosity=None, no_colors=None, log=None):
        self.spotify = None
        self.log = log if log is not None else os.getenv(MB_LOG, str(DEFAULT_LOG))
        self.quiet = quiet if quiet is not None else lib.str2bool(os.getenv(MB_QUIET, str(DEFAULT_QUIET)))
        self.debug = debug if debug is not None else lib.str2bool(os.getenv(MB_DEBUG, str(DEFAULT_DEBUG)))
        self.timings = timings if timings is not None else lib.str2bool(os.getenv(MB_TIMINGS, str(DEFAULT_TIMINGS)))
        self.dry = dry if dry is not None else lib.str2bool(os.getenv(MB_DRY, str(DEFAULT_DRY)))
        self.no_colors = no_colors if no_colors is not None else lib.str2bool(os.getenv(MB_NO_COLORS, str(DEFAULT_NO_COLORS)))
        self.verbosity = verbosity if verbosity is not None else os.getenv(MB_VERBOSITY, DEFAULT_VERBOSITY)

        if self.timings:
            self.verbosity = 'info'
            self.quiet = True
        if self.debug:
            self.verbosity = 'debug'
            self.quiet = True
        if self.verbosity == 'debug':
            loop = asyncio.get_event_loop()
            loop.set_debug(True)
            # triggers : "'NoneType' object has no attribute 'co_filename'
            # loop.slow_callback_duration = 0.001
            loop.slow_callback_duration = 0.005

        self.level = verbosities[self.verbosity]
        logging.basicConfig(level=self.level, format=self.fmt)
        if not self.no_colors:
            coloredlogs.install(level=self.level, fmt=self.fmt)

        if self.log is not None:
            if check_file_writable(self.log):
                fh = logging.FileHandler(self.log)
                fh.setLevel(logging.DEBUG)
                logging.getLogger().addHandler(fh)
            else:
                logger.warning('No permission to write to %s for current user %s', self.log, current_user)
        logger.debug(self)

    def __repr__(self):
        fmt = 'log:{} timings:{} debug:{} quiet:{} dry:{} verbosity:{} no_colors:{}'
        return fmt.format(self.log, self.timings, self.debug, self.quiet, self.dry, self.verbosity, self.no_colors)


config = Config()
