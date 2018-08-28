# -*- coding: utf-8 -*-
import click
import asyncio
import os
import coloredlogs
import logging
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL, getLogger, FileHandler
from . import lib

logger = logging.getLogger(__name__)

DEFAULT_LOG = '/var/log/musicbot.log'
DEFAULT_VERBOSITY = 'warning'
DEFAULT_DRY = False
DEFAULT_QUIET = False
DEFAULT_DEBUG = False
DEFAULT_NO_COLORS = False
DEFAULT_TIMINGS = False
verbosities = {'debug': DEBUG,
               'info': INFO,
               'warning': WARNING,
               'error': ERROR,
               'critical': CRITICAL}

options = [
    click.option('--log', help='Log file path', type=click.Path(), envvar='MB_LOG', default=DEFAULT_LOG, show_default=True),
    click.option('--debug', help='Be very verbose, same as --verbosity debug + hide progress bars', envvar='MB_DEBUG', default=DEFAULT_DEBUG, is_flag=True),
    click.option('--timings', help='Set verbosity to info and show execution timings', envvar='MB_TIMINGS', default=DEFAULT_DEBUG, is_flag=True),
    click.option('--verbosity', help='Verbosity levels', envvar='MB_VERBOSITY', default=DEFAULT_VERBOSITY, type=click.Choice(verbosities.keys()), show_default=True),
    click.option('--dry', help='Take no real action', envvar='MB_DRY', default=DEFAULT_DRY, is_flag=True),
    click.option('--quiet', help='Disable progress bars', envvar='MB_QUIET', default=DEFAULT_QUIET, is_flag=True),
    click.option('--no-colors', help='Disable colorized output', envvar='MB_NO_COLORS', default=DEFAULT_NO_COLORS, is_flag=True),
]


class Config(object):
    def __init__(self):
        self.log = DEFAULT_LOG
        self.quiet = DEFAULT_QUIET
        self.debug = DEFAULT_DEBUG
        self.timings = DEFAULT_TIMINGS
        self.dry = DEFAULT_DRY
        self.no_colors = DEFAULT_NO_COLORS
        self.verbosity = DEFAULT_VERBOSITY
        self.fmt = "%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s"

    def set(self, debug=None, timings=None, dry=None, quiet=None, verbosity=None, no_colors=None, log=None):
        self.log = log if log is not None else os.getenv('MB_LOG', DEFAULT_LOG)
        self.quiet = quiet if quiet is not None else lib.str2bool(os.getenv('MB_QUIET', DEFAULT_QUIET))
        self.debug = debug if debug is not None else lib.str2bool(os.getenv('MB_DEBUG', DEFAULT_DEBUG))
        self.timings = timings if timings is not None else lib.str2bool(os.getenv('MB_TIMINGS', DEFAULT_TIMINGS))
        self.dry = dry if dry is not None else lib.str2bool(os.getenv('MB_DRY', DEFAULT_DRY))
        self.no_colors = no_colors if no_colors is not None else lib.str2bool(os.getenv('MB_NO_COLORS', DEFAULT_NO_COLORS))
        self.verbosity = verbosity if verbosity is not None else os.getenv('MB_VERBOSITY', DEFAULT_VERBOSITY)

        if self.timings:
            self.verbosity = 'info'
            self.quiet = True
        if self.debug:
            self.verbosity = 'debug'
            self.quiet = True
        if self.verbosity == 'debug':
            loop = asyncio.get_event_loop()
            loop.set_debug(True)

        level = verbosities[self.verbosity]
        logging.basicConfig(level=level, format=self.fmt)
        if not self.no_colors:
            coloredlogs.install(level=level, fmt=self.fmt)

        if self.log is not None:
            fh = FileHandler(self.log)
            fh.setLevel(DEBUG)
            getLogger().addHandler(fh)

    def __repr__(self):
        fmt = 'log:{} timings:{} debug:{} quiet:{} dry:{} verbosity:{} no_colors:{}'
        return fmt.format(self.log, self.timings, self.debug, self.quiet, self.dry, self.verbosity, self.no_colors)


config = Config()
