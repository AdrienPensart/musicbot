# -*- coding: utf-8 -*-
import click
import asyncio
import os
import uuid
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL, getLogger, debug
from . import lib

DEFAULT_VERBOSITY = 'error'
DEFAULT_DRY = False
DEFAULT_QUIET = False
verbosities = {'debug': DEBUG,
               'info': INFO,
               'warning': WARNING,
               'error': ERROR,
               'critical': CRITICAL}

options = [
    click.option('--verbosity', help='Verbosity levels', envvar='MB_VERBOSITY', default=DEFAULT_VERBOSITY, type=click.Choice(verbosities.keys())),
    click.option('--dry', help='Take no real action', envvar='MB_DRY', default=DEFAULT_DRY, is_flag=True),
    click.option('--quiet', help='Silence any output (like progress bars)', envvar='MB_QUIET', default=DEFAULT_QUIET, is_flag=True),
    click.option('--invocation', help='Invocation ID, resumable execution (experimental)', default=uuid.uuid4()),
]


class Config(object):
    def __init__(self, **kwargs):
        self.set(**kwargs)

    def set(self, invocation=None, dry=None, quiet=None, verbosity=None, **kwargs):
        self.quiet = quiet if quiet is not None else lib.str2bool(os.getenv('MB_QUIET', DEFAULT_QUIET))
        self.dry = dry if dry is not None else lib.str2bool(os.getenv('MB_DRY', DEFAULT_DRY))
        self.verbosity = verbosity if verbosity is not None else os.getenv('MB_VERBOSITY', DEFAULT_VERBOSITY)
        self.invocation = invocation if invocation is not None else os.getenv('MB_INVOCATION', uuid.uuid4())
        debug(self)

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
            debug('Loop debugging enabled')
            loop.set_debug(True)
        debug('new verbosity: {}'.format(verbosity))

    def __repr__(self):
        return 'invocation:{} quiet:{} dry:{} verbosity:{}'.format(self.invocation, self.quiet, self.dry, self._verbosity)


config = Config()
