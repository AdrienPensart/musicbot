# -*- coding: utf-8 -*-
import click
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL, getLogger, debug

verbosities = {'debug': DEBUG,
               'info': INFO,
               'warning': WARNING,
               'error': ERROR,
               'critical': CRITICAL}


class Config(object):
    def __init__(self):
        self.quiet = False
        self.dry = False
        # self._verbosity = ERROR
        self._verbosity = WARNING

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
        debug('new verbosity: {}'.format(verbosity))

    def __repr__(self):
        return '{} {} {}'.format(self.quiet, self.dry, self._verbosity)


global_options = [
    click.option('--verbosity', help='Verbosity levels', default='error', type=click.Choice(verbosities.keys())),
    click.option('--dry', help='Take no real action', default=False, is_flag=True),
    click.option('--quiet', help='Silence any output (like progress bars)', default=False, is_flag=True)
]

config = Config()
