# -*- coding: utf-8 -*-
import click
import os
import logging
from .. import lib

logger = logging.getLogger(__name__)

DEFAULT_DEV = False
DEFAULT_WATCHER = False
DEFAULT_AUTOSCAN = False
DEFAULT_SERVER_CACHE = False
DEFAULT_CLIENT_CACHE = False
DEFAULT_NO_AUTH = False

options = [
    click.option('--dev', envvar='MB_DEV', help='Watch for source file modification', default=DEFAULT_DEV, is_flag=True),
    click.option('--watcher', envvar='MB_WATCHER', help='Watch for music file modification', default=DEFAULT_WATCHER, is_flag=True),
    click.option('--autoscan', envvar='MB_AUTOSCAN', help='Enable auto scan background job', default=DEFAULT_AUTOSCAN, is_flag=True),
    click.option('--server-cache', envvar='MB_SERVER_CACHE', help='Activate server cache system', default=DEFAULT_SERVER_CACHE, is_flag=True),
    click.option('--client-cache', envvar='MB_CLIENT_CACHE', help='Activate client cache system', default=DEFAULT_CLIENT_CACHE, is_flag=True),
    click.option('--no-auth', envvar='MB_NO_AUTH', help='Disable authentication system', default=DEFAULT_NO_AUTH, is_flag=True),
]


class WebConfig:
    def __init__(self, **kwargs):
        self.set(**kwargs)

    def set(self, dev=None, autoscan=None, watcher=None, client_cache=None, server_cache=None, no_auth=None):
        self.dev = dev if dev is not None else lib.str2bool(os.getenv('MB_DEV', str(DEFAULT_DEV)))
        self.watcher = watcher if watcher is not None else lib.str2bool(os.getenv('MB_WATCHER', str(DEFAULT_WATCHER)))
        self.autoscan = autoscan if autoscan is not None else lib.str2bool(os.getenv('MB_AUTOSCAN', str(DEFAULT_AUTOSCAN)))
        self.server_cache = server_cache if server_cache is not None else lib.str2bool(os.getenv('MB_SERVER_CACHE', str(DEFAULT_SERVER_CACHE)))
        self.client_cache = client_cache if client_cache is not None else lib.str2bool(os.getenv('MB_CLIENT_CACHE', str(DEFAULT_CLIENT_CACHE)))
        self.no_auth = no_auth if no_auth is not None else lib.str2bool(os.getenv('MB_NO_AUTH', str(DEFAULT_NO_AUTH)))
        logger.debug('Webconfig: %s', self)

    def __repr__(self):
        return 'dev:{} watcher:{} autoscan:{} server_cache:{} client_cache:{} no_auth:{}'.format(self.dev, self.watcher, self.autoscan, self.server_cache, self.client_cache, self.no_auth)


webconfig = WebConfig()
