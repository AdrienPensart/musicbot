# -*- coding: utf-8 -*-
import click
from logging import debug
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL, basicConfig, getLogger
from singleton_decorator import singleton

verbosities = {'debug': DEBUG,
               'info': INFO,
               'warning': WARNING,
               'error': ERROR,
               'critical': CRITICAL}


@singleton
class Config(object):
    quiet = False,
    dry = False,
    verbosity = 'error'
    level = ERROR

    def __init__(self, **kwargs):
        Config.verbosity = kwargs['verbosity']
        Config.dry = kwargs['dry']
        Config.quiet = kwargs['quiet']
        Config.level = verbosities[Config.verbosity]
        basicConfig(level=Config.level)
        getLogger('asyncio').setLevel(Config.level)
        debug('context: {} {} {}'.format(Config.quiet, Config.dry, Config.verbosity))

    def isDebug(self):
        return Config.level is DEBUG


global_options = [
    click.option('--verbosity', help='Verbosity levels', default='error', type=click.Choice(verbosities.keys())),
    click.option('--dry', help='Take no real action', default=False, is_flag=True),
    click.option('--quiet', help='Silence any output (like progress bars)', default=False, is_flag=True)
]
