# -*- coding: utf-8 -*-
import click
import os

options = [
    click.option('--dev', envvar='MB_DEV', help='Watch for source file modification', is_flag=True),
    click.option('--watcher', envvar='MB_WATCHER', help='Watch for music file modification', is_flag=True),
    click.option('--autoscan', envvar='MB_AUTOSCAN', help='Enable auto scan background job', is_flag=True),
    click.option('--server-cache', envvar='MB_SERVER_CACHE', help='Activate server cache system', is_flag=True),
    click.option('--client-cache', envvar='MB_CLIENT_CACHE', help='Activate client cache system', is_flag=True),
]


class WebConfig(object):
    def __init__(self, **kwargs):
        self.set(**kwargs)

    def set(self, dev=None, autoscan=None, watcher=None, client_cache=None, server_cache=None, **kwargs):
        self.dev = dev if dev is not None else os.getenv('MB_DEV', False)
        self.watcher = watcher if watcher is not None else os.getenv('MB_WATCHER', False)
        self.autoscan = autoscan if autoscan is not None else os.getenv('MB_AUTOSCAN', False)
        self.server_cache = server_cache if server_cache is not None else os.getenv('MB_SERVER_CACHE', False)
        self.client_cache = client_cache if client_cache is not None else os.getenv('MB_CLIENT_CACHE', False)


webconfig = WebConfig()
