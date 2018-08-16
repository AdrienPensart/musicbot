# -*- coding: utf-8 -*-
import click
import asyncio
import os
import uuid
import coloredlogs
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL, getLogger, FileHandler
from logging import debug as print_debug
from . import lib

DEFAULT_LOG = '/var/log/musicbot.log'
DEFAULT_VERBOSITY = 'error'
DEFAULT_DRY = False
DEFAULT_QUIET = False
DEFAULT_DEBUG = False
DEFAULT_NO_COLOR = False
verbosities = {'debug': DEBUG,
               'info': INFO,
               'warning': WARNING,
               'error': ERROR,
               'critical': CRITICAL}

options = [
    click.option('--log', help='Log file path', type=click.Path(), envvar='RC_LOG', default=DEFAULT_LOG, show_default=True),
    click.option('--debug', help='Be very verbose, same as --verbosity debug + hide progress bars', envvar='RC_DEBUG', default=DEFAULT_DEBUG, is_flag=True),
    click.option('--verbosity', help='Verbosity levels', envvar='MB_VERBOSITY', default=DEFAULT_VERBOSITY, type=click.Choice(verbosities.keys()), show_default=True),
    click.option('--dry', help='Take no real action', envvar='MB_DRY', default=DEFAULT_DRY, is_flag=True),
    click.option('--quiet', help='Disable progress bars', envvar='MB_QUIET', default=DEFAULT_QUIET, is_flag=True),
    click.option('--no-color', help='Disable colorized output', envvar='RC_NO_COLOR', default=DEFAULT_NO_COLOR, is_flag=True),
    click.option('--invocation', help='Resumable execution ID (experimental)', default=uuid.uuid4()),
]


class Config(object):
    def __init__(self, **kwargs):
        self.set(**kwargs)
        fh = FileHandler(self.log)
        fh.setLevel(DEBUG)
        getLogger().addHandler(fh)

    def set(self, debug=None, invocation=None, dry=None, quiet=None, verbosity=None, no_color=None, log=None, **kwargs):
        self.log = log if log is not None else os.getenv('RC_LOG', DEFAULT_LOG)
        self.quiet = quiet if quiet is not None else lib.str2bool(os.getenv('MB_QUIET', DEFAULT_QUIET))
        self.dry = dry if dry is not None else lib.str2bool(os.getenv('MB_DRY', DEFAULT_DRY))
        self.no_color = no_color if no_color is not None else lib.str2bool(os.getenv('RC_NO_COLOR', DEFAULT_NO_COLOR))
        self.verbosity = verbosity if verbosity is not None else os.getenv('MB_VERBOSITY', DEFAULT_VERBOSITY)
        self.invocation = invocation if invocation is not None else os.getenv('MB_INVOCATION', uuid.uuid4())
        if debug:
            self.verbosity = 'debug'
            self.quiet = True
        if not self.no_color:
            coloredlogs.install(level=self._verbosity, fmt="%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s")
        print_debug(self)

    def isDebug(self):
        return self._verbosity is DEBUG

    @property
    def verbosity(self):
        return self._verbosity

    @verbosity.setter
    def verbosity(self, verbosity):
        self._verbosity = verbosity
        level = verbosities[verbosity]
        getLogger().setLevel(level)
        getLogger('asyncio').setLevel(level)
        getLogger('sanic').setLevel(level)
        loop = asyncio.get_event_loop()
        if level is DEBUG:
            print_debug('Loop debugging enabled')
            loop.set_debug(True)
        print_debug('new verbosity: {}'.format(verbosity))

    def __repr__(self):
        return 'invocation:{} quiet:{} dry:{} verbosity:{} no_color:{}'.format(self.invocation, self.quiet, self.dry, self._verbosity, self.no_color)

config = Config()
