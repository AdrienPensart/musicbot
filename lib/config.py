# -*- coding: utf-8 -*-
import click
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL, basicConfig, getLogger

verbosities = {'debug': DEBUG,
               'info': INFO,
               'warning': WARNING,
               'error': ERROR,
               'critical': CRITICAL}


class Config(object):
    quiet = False,
    dry = False,
    verbosity = 'error'
    level = ERROR

    def __init__(self, verbosity='error', dry=False, quiet=False):
        self.verbosity = verbosity
        self.dry = dry
        self.quiet = quiet
        self.level = verbosities[verbosity]
        basicConfig(level=self.level)
        getLogger('asyncio').setLevel(self.level)

    def isDebug(self):
        return Config.level is DEBUG


global_options = [
    click.option('--verbosity', help='Verbosity levels', default='error', type=click.Choice(verbosities.keys())),
    click.option('--dry', help='Take no real action', default=False, is_flag=True),
    click.option('--quiet', help='Silence any output (like progress bars)', default=False, is_flag=True)
]

config = Config()
