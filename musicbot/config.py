import os
import logging
import pwd
import attr
import click
import coloredlogs
from . import lib

logger = logging.getLogger(__name__)
current_user = pwd.getpwuid(os.getuid()).pw_name

DEFAULT_LOG = '/var/log/musicbot.log'
MB_LOG = 'MB_LOG'
MB_INFO = 'MB_INFO'
MB_DEBUG = 'MB_DEBUG'
MB_TIMINGS = 'MB_TIMINGS'
MB_VERBOSITY = 'MB_VERBOSITY'
MB_DRY = 'MB_DRY'
MB_QUIET = 'MB_QUIET'
MB_COLORS = 'MB_COLORS'

DEFAULT_VERBOSITY = 'warning'
DEFAULT_DRY = False
DEFAULT_QUIET = False
DEFAULT_DEBUG = False
DEFAULT_COLORS = True
DEFAULT_TIMINGS = False
DEFAULT_INFO = False


verbosities = {'debug': logging.DEBUG,
               'info': logging.INFO,
               'warning': logging.WARNING,
               'error': logging.ERROR,
               'critical': logging.CRITICAL}

options = [
    click.option('--log', '-l', help='Log file path', type=click.Path(), envvar=MB_LOG, default=DEFAULT_LOG, show_default=True),
    click.option('--info', '-i', help='Same as --verbosity info"', envvar=MB_INFO, default=DEFAULT_INFO, is_flag=True, show_default=False),
    click.option('--debug', '-d', help='Be very verbose, same as --verbosity debug + hide progress bars', envvar=MB_DEBUG, default=DEFAULT_DEBUG, is_flag=True, show_default=True),
    click.option('--timings', '-t', help='Set verbosity to info and show execution timings', envvar=MB_TIMINGS, default=DEFAULT_TIMINGS, is_flag=True, show_default=True),
    click.option('--verbosity', '-v', help='Verbosity levels', envvar=MB_VERBOSITY, default=DEFAULT_VERBOSITY, type=click.Choice(verbosities.keys()), show_default=True),
    click.option('--dry', help='Take no real action', envvar=MB_DRY, default=DEFAULT_DRY, is_flag=True, show_default=True),
    click.option('--quiet', '-q', help='Disable progress bars', envvar=MB_QUIET, default=DEFAULT_QUIET, is_flag=True, show_default=True),
    click.option('--colors/--no-colors', help='Disable colorized output', envvar=MB_COLORS, default=DEFAULT_COLORS, show_default=True),
]


def check_file_writable(fnm):
    if os.path.exists(fnm):
        # path exists
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
    dry = attr.ib(default=DEFAULT_DRY)
    colors = attr.ib(default=DEFAULT_COLORS)
    verbosity = attr.ib(default=DEFAULT_VERBOSITY)
    level = attr.ib(default=verbosities[DEFAULT_VERBOSITY])
    fmt = attr.ib(default="%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s")

    def set(self, debug=None, info=None, timings=None, dry=None, quiet=None, verbosity=None, colors=None, log=None):
        self.log = log if log is not None else os.getenv(MB_LOG, str(DEFAULT_LOG))
        self.quiet = quiet if quiet is not None else lib.str2bool(os.getenv(MB_QUIET, str(DEFAULT_QUIET)))
        self.debug = debug if debug is not None else lib.str2bool(os.getenv(MB_DEBUG, str(DEFAULT_DEBUG)))
        self.info = info if info is not None else lib.str2bool(os.getenv(MB_INFO, str(DEFAULT_INFO)))
        self.timings = timings if timings is not None else lib.str2bool(os.getenv(MB_TIMINGS, str(DEFAULT_TIMINGS)))
        self.dry = dry if dry is not None else lib.str2bool(os.getenv(MB_DRY, str(DEFAULT_DRY)))
        self.colors = colors if colors is not None else lib.str2bool(os.getenv(MB_COLORS, str(DEFAULT_COLORS)))
        self.verbosity = verbosity if verbosity is not None else os.getenv(MB_VERBOSITY, DEFAULT_VERBOSITY)

        if self.timings or self.info:
            self.verbosity = 'info'
            self.quiet = True
        if self.debug:
            self.verbosity = 'debug'
            self.quiet = True

        self.level = verbosities[self.verbosity]
        logging.basicConfig(level=self.level, format=self.fmt)
        if self.colors:
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
        fmt = 'log:{} timings:{} debug:{} quiet:{} dry:{} verbosity:{} colors:{}'
        return fmt.format(self.log, self.timings, self.debug, self.quiet, self.dry, self.verbosity, self.colors)


config = Config()
